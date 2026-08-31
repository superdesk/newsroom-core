from typing import Any
from urllib.parse import urlencode

from pydantic import AliasChoices

from content_api.errors import UnexpectedParameterError, BadParameterValueError
from superdesk.flask import request as flask_request
from superdesk.core.types.web import Request, Response
from superdesk.core import get_app_config

from newsroom.types import SectionEnum
from newsroom.types.wire import WireItem
from newsroom.wire.service import WireItemService
from newsroom.wire.embeds import (
    apply_company_permissions_to_embeds,
    update_embed_urls,
    remove_all_embeds,
    remove_internal_renditions,
)
from newsroom.search.types import NewshubSearchRequest, SearchFilterFunction
from newsroom.search.base_service import BaseNewshubSearchService
from newsroom.news_api.utils import post_api_audit, format_api_date
from newsroom.search.filters import apply_company_filter, apply_section_filter, apply_products_filter

from .filters import (
    apply_date_filter,
    apply_filter_fields,
    apply_projection,
    apply_request_filter,
    prefill_company,
    prefill_products,
    validate_page,
    prefill_search_latest_version,
    apply_api_limit_filter,
)
from .types import NewsApiSearchRequestArgs

default_search_filters: list[SearchFilterFunction] = [
    prefill_company,
    prefill_products,
    prefill_search_latest_version,
    apply_section_filter,
    apply_company_filter,
    apply_products_filter,
    apply_filter_fields,
    apply_date_filter,
    apply_api_limit_filter,
    apply_request_filter,
    apply_projection,
    validate_page,
]


class NewsApiSearchServiceAsync(BaseNewshubSearchService[NewsApiSearchRequestArgs, WireItem]):
    search_args_class = NewsApiSearchRequestArgs
    filters = default_search_filters
    section = SectionEnum.NEWS_API
    default_sort = [{"versioncreated", 1}]
    default_page_size = 25

    def __init__(self):
        self.service = WireItemService()

    async def process_web_request(self, request: Request):
        self._validate_first_page(request)
        self._validate_unknown_fields()
        resp = await super().process_web_request(request)

        await self.process_post_api_audit(request, resp)
        await self.process_response_enhancements(request, resp)

        return resp

    def _validate_first_page(self, request: Request):
        """
        Ensures that if a page number is provided in the URL, it is a valid integer >= 1.
        (Note: 1-indexed pagination is enforced; missing page arguments default to 1 downstream).
        """
        page = request.get_url_arg("page")
        if page is not None:
            try:
                if int(page) < 1:
                    raise BadParameterValueError(desc="Page number must be greater than or equal to 1")
            except ValueError:
                raise BadParameterValueError(desc="Page number must be a valid integer")

    def _validate_unknown_fields(self):
        """
        Since we construct the search request using `from_url_args` we cannot get all the arguments
        provided in the url, therefore we validate here all the model fields (allowed ones) against
        those coming from the request. If any unknown found, it raises an error
        """
        model = self.search_args_class()
        url_args: set[str] = set(flask_request.args.keys()) - {"token"}
        allowed_fields = set(model.model_fields.keys())

        for field, info in model.model_fields.items():
            if isinstance(info.validation_alias, AliasChoices):
                # Exclude `AliasPath` instances from choices, as we won't be able to
                # translate that into a field name
                allowed_fields |= set([choice for choice in info.validation_alias.choices if isinstance(choice, str)])
            else:
                allowed_fields.add(info.alias or field)

        unknown_fields = url_args - allowed_fields
        if unknown_fields:
            raise UnexpectedParameterError(desc=f"Unexpected parameter(s): {', '.join(unknown_fields)}")

    async def process_post_api_audit(self, request: Request, response: Response):
        await post_api_audit(
            request,
            [item["_id"] for item in response.body.get("_items") or [] if item.get("_id")],
        )

    async def process_response_enhancements(self, request: Request, response: Response):
        search_req = self.get_search_request_instance(request)
        self.build_hateoas(request, response, search_req)

        # If a date format has been configured then apply it to date fields
        date_format = get_app_config("API_DATE_FORMAT")

        for doc in response.body["_items"] or []:
            if date_format:
                for date_field in ["firstcreated", "versioncreated", "embargoed"]:
                    date_value = doc.get(date_field)
                    if isinstance(date_value, str) and date_value:
                        doc[date_field] = format_api_date(date_value)

            self._enhance_internal_item_hateoas(doc)

            if get_app_config("WIRE_EMBED_PERMISSIONS", True):
                # set the references in the document to absolute values
                if "associations" in (search_req.args.include_fields or []):
                    # apply the filtering to any media in the doc
                    await apply_company_permissions_to_embeds([doc], SectionEnum.NEWS_API)

                    remove_internal_renditions(doc)
                    await update_embed_urls(doc, None)
                else:
                    remove_all_embeds(doc)

    def build_hateoas(self, req: Request, resp: Response, search_req: NewshubSearchRequest[NewsApiSearchRequestArgs]):
        base_url = req.path.strip("/").replace(get_app_config("URL_PREFIX"), "")
        original_args = req.request.args.to_dict()

        resp.body.setdefault("_links", {})
        resp.body["_links"]["parent"] = {"title": "Home", "href": "/"}

        resp.body["_links"]["self"] = {
            "title": "News Search",
            "href": f"{base_url}?{urlencode(original_args)}" if original_args else base_url,
        }

        total_items = resp.body.get("_meta", {}).get("total", 0)
        current_page = search_req.args.page if search_req.args.page > 0 else 1
        resp.body["_meta"]["page"] = current_page
        page_size = search_req.args.page_size

        # add next page if there are more items
        if (current_page * page_size) < total_items:
            next_args = {**original_args, "page": current_page + 1}
            resp.body["_links"]["next"] = {"title": "next page", "href": f"{base_url}?{urlencode(next_args)}"}

        # add prev page if needed
        if current_page > 1:
            prev_args = {**original_args, "page": current_page - 1}
            resp.body["_links"]["prev"] = {"title": "prev page", "href": f"{base_url}?{urlencode(prev_args)}"}

        if total_items > 0:
            last_page = (total_items + page_size - 1) // page_size
            last_args = {**original_args, "page": last_page}
            resp.body["_links"]["last"] = {"title": "last page", "href": f"{base_url}?{urlencode(last_args)}"}

    def _enhance_internal_item_hateoas(self, item: dict[str, Any]):
        item.setdefault("_links", {})
        item["_links"]["self"] = {
            "href": f"news/item/{item['_id']}",
            "title": "News Item",
        }
