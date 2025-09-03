from lxml.html import HtmlElement
from quart_babel import gettext

from superdesk.core import get_app_config
from superdesk.core.types import Request
from superdesk.core.resources.cursor import ElasticsearchResourceCursorAsync
from superdesk.flask import request as flask_request, url_for

from typing import Any, Set
from newsroom.types import NewsApiAuditResourceModel, CompanyResource
from newsroom.exceptions import AuthorizationError
from newsroom.settings import get_setting
from newsroom.utils import update_embeds_in_body


async def post_api_audit(request: Request, item_ids: list[str]) -> None:
    audit_doc = NewsApiAuditResourceModel(
        items_id=item_ids,
        uri=request.url,
        endpoint=request.endpoint.name,
        remote_addr=flask_request.access_route[0] if flask_request.access_route else flask_request.remote_addr,
    )

    company_id = request.storage.request.get("company_id")
    if company_id:
        audit_doc.subscriber = company_id

    await NewsApiAuditResourceModel.get_service().create([audit_doc])


def format_report_results(
    search_result: ElasticsearchResourceCursorAsync[NewsApiAuditResourceModel],
    unique_endpoints: list[str],
    companies: dict[str, CompanyResource],
) -> dict[str, dict[str, int]]:
    aggs = (search_result.hits or {}).get("aggregations") or {}
    buckets = (aggs.get("items") or {}).get("buckets") or []
    results: dict[str, dict[str, int]] = {}

    for bucket in buckets:
        try:
            company = companies[bucket["key"]]
            if not company:
                continue
            results[company.name] = {}
            for endpoint_bucket in bucket["endpoints"]["buckets"]:
                results[company.name][endpoint_bucket["key"]] = endpoint_bucket["doc_count"]
                if endpoint_bucket["key"] not in unique_endpoints:
                    unique_endpoints.append(endpoint_bucket["key"])
        except (KeyError, TypeError, IndexError):
            continue

    return results


def remove_internal_renditions(item: dict[str, Any], remove_media=False) -> dict[str, Any]:
    """
    Remove the internal and original image renditions from the feature media and embedded media. The media can
    optionally be removed as we do not serve this on the api.
    :param item:
    :param remove_media:
    :return:
    """
    allowed_renditions_setting = get_setting("news_api_allowed_renditions")
    if not allowed_renditions_setting:
        return item

    allowed_pic_renditions: Set[str] = set(s.strip() for s in allowed_renditions_setting.split(",") if s.strip())

    for association_key, association_item in item.get("associations", {}).items():
        if not association_item:
            continue
        clean_renditions: dict[str, Any] = dict()
        for key, rendition in association_item.get("renditions", {}).items():
            if association_item.get("type") == "picture":
                if key in allowed_pic_renditions:
                    if remove_media:
                        rendition.pop("media", None)
                    clean_renditions[key] = rendition
            else:
                clean_renditions[key] = rendition

        item["associations"][association_key]["renditions"] = clean_renditions

        if isinstance(association_item, dict):
            association_item.pop("products", None)
            association_item.pop("subscribers", None)

    return item


def get_company_from_newsapi_request(request: Request) -> CompanyResource:
    company = request.storage.request.get("company_instance")
    if company is None or (company and not company.is_enabled):
        raise AuthorizationError(403, gettext("Company not found or not enabled."))

    return company


def update_embed_urls(item: dict[str, Any], token: str | None = None):
    """
    Update the urls in the embeds to the endpoint that allows logging of the item that the embed belongs to
    :param item:
    :param token:
    :return:
    """

    def update_embed(item: dict[str, Any], elem: HtmlElement, group: str):
        embed_id = "editor_" + group

        rendition_map = {"audio": "original", "video": "original", "img": "16-9"}
        rendition = rendition_map.get(elem.tag)

        src = None
        if rendition:
            src = item.get("associations", {}).get(embed_id, {}).get("renditions", {}).get(rendition)

        if src is None:
            return

        url_kwargs = {
            "asset_id": src.get("media"),
            "item_id": item.get("_id"),
            "_external": True,
        }

        # Determine the endpoint and add token if present
        if token:
            endpoint_name = "assets.download"
            url_kwargs["token"] = token
        else:
            endpoint_name = "assets.get_item"

        # Assign the generated URL to the element's 'src' attribute
        if src is not None and elem is not None:
            elem.attrib["src"] = url_for(endpoint_name, **url_kwargs)
            return True  # Return True if assignment happened
        return False  # Return False if src or elem was None

    update_embeds_in_body(item, update_embed, update_embed, update_embed)


def set_association_links(item):
    """
    Updates the links in the associations to the endpoint that logs the download
    :param item:
    :return:
    """
    if not get_app_config("EMBED_PRODUCT_FILTERING"):
        return

    for key, ass in item.get("associations", {}).items():
        if isinstance(ass, dict) and not key == "featuremedia":
            for rendition in ass.get("renditions"):
                if ass.get("renditions", {}).get(rendition, {}).get("href"):
                    ass.get("renditions", {}).get(rendition, {})["href"] = (
                        ass.get("renditions", {}).get(rendition, {}).get("href") + "?item_id=" + item.get("_id")
                    )
