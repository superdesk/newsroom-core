from typing import Any
from urllib.parse import urlencode

from werkzeug.datastructures import ImmutableMultiDict

from content_api.errors import UnexpectedParameterError
from superdesk.flask import request as flask_request
from superdesk.core.types.web import Request, Response

from newsroom.types import SectionEnum
from newsroom.types.wire import WireItem
from newsroom.wire.service import WireItemService
from newsroom.auth.utils import get_company_or_none_from_request
from newsroom.products.utils import get_products_by_company_async
from newsroom.search.types import NewshubSearchRequest, SearchFilterFunction
from newsroom.search.base_service import BaseNewshubSearchService
from newsroom.news_api.utils import check_association_permission, post_api_audit, remove_internal_renditions
from newsroom.search.filters import apply_company_filter, apply_section_filter, apply_products_filter

from .filters import (
    apply_date_filter,
    apply_filter_fields,
    apply_projection,
    apply_request_filter,
    prefill_company,
    prefill_products,
    validate_page,
)
from .types import NewsApiSearchRequestArgs


default_search_filters: list[SearchFilterFunction] = [
    prefill_company,
    prefill_products,
    apply_section_filter,
    apply_company_filter,
    apply_products_filter,
    apply_filter_fields,
    apply_date_filter,
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
        self._validate_unknown_fields()
        resp = await super().process_web_request(request)

        await self.process_post_api_audit(request, resp)
        await self.process_response_enhancements(request, resp)

        return resp

    def _validate_unknown_fields(self):
        """
        Since we construct the search request using `from_url_args` we cannot get all the arguments
        provided in the url, therefore we validate here all the model fields (allowed ones) against
        those coming from the request. If any unknown found, it raises an error
        """
        model = self.search_args_class()
        url_args: ImmutableMultiDict = flask_request.args
        allowed_fields = set(model.model_fields.keys())

        for field in model.model_fields.values():
            if field.validation_alias:
                for alias in field.validation_alias.choices:
                    allowed_fields.add(alias)

        unknown_fields = set(url_args.keys()) - allowed_fields
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

        company = get_company_or_none_from_request(request)
        assert company is not None
        products = [
            product.to_dict()
            for product in await get_products_by_company_async(company, product_type=SectionEnum.NEWS_API)
        ]

        for doc in response.body["_items"] or []:
            self._enhance_internal_item_hateoas(doc)

            if "associations" in (search_req.args.include_fields or []):
                self._check_associations(doc, products)

    def _check_associations(self, doc: dict[str, Any], products: list[dict[str, Any]]):
        if not check_association_permission(doc, products):
            doc.pop("associations", None)
        else:
            remove_internal_renditions(doc)

    def build_hateoas(self, req: Request, resp: Response, search_req: NewshubSearchRequest[NewsApiSearchRequestArgs]):
        base_url = req.path.strip("/")
        query_params = search_req.args.to_dict(flatten_lists=True)

        resp.body.setdefault("_links", {})
        resp.body["_links"]["parent"] = {"title": "Home", "href": "/"}

        # append page and page_size only if they were provided in original request
        for arg in ["page", "page_size"]:
            if arg in flask_request.view_args:
                query_params.update({arg: query_params.get(arg)})

        q_args = f"?{urlencode(query_params)}" if query_params else ""
        resp.body["_links"]["self"] = (
            {
                "title": "News Search",
                "href": f"{base_url}{q_args}",
            },
        )

        # add next page if there are more items
        if (search_req.args.page * search_req.args.page_size) < resp.body["_meta"]["total"]:
            query_params["page"] = search_req.args.page + 1
            resp.body["_links"]["next"] = {"title": "next page", "href": f"{base_url}?{urlencode(query_params)}"}

        # add prev page if needed
        if search_req.args.page > 1:
            query_params["page"] = search_req.args.page - 1
            resp.body["_links"]["prev"] = {"title": "prev page", "href": f"{base_url}?{urlencode(query_params)}"}

    def _enhance_internal_item_hateoas(self, item: dict[str, Any]):
        item.setdefault("_links", {})
        item["_links"]["self"] = {
            "href": f"news/item/{item['_id']}",
            "title": "News Item",
        }
