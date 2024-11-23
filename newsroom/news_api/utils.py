from quart_babel import gettext

from superdesk.core import get_app_config
from superdesk.core.types import Request
from superdesk.core.resources.cursor import ElasticsearchResourceCursorAsync
from superdesk.flask import request as flask_request

from newsroom.types import NewsApiAuditResourceModel, CompanyResource
from newsroom.exceptions import AuthorizationError


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


def remove_internal_renditions(item):
    clean_renditions = dict()

    # associations featuremedia will contain the internal newsroom renditions, we need to remove these.
    if ((item.get("associations") or {}).get("featuremedia") or {}).get("renditions"):
        for key, rendition in item["associations"]["featuremedia"]["renditions"].items():
            if not key.startswith("_newsroom"):
                rendition.pop("media", None)
                clean_renditions[key] = rendition

        item["associations"]["featuremedia"]["renditions"] = clean_renditions
    for key, meta in item.get("associations", {}).items():
        if isinstance(meta, dict):
            meta.pop("products", None)
            meta.pop("subscribers", None)

    return item


def check_association_permission(item, products):
    """
    Check if any of the products that the passed image item matches are permissioned superdesk products for the
     company
    :param item:
    :return:
    """
    if not get_app_config("NEWS_API_IMAGE_PERMISSIONS_ENABLED"):
        return True

    if ((item.get("associations") or {}).get("featuremedia") or {}).get("products"):
        # Extract the products that the image matched in Superdesk
        im_products = [
            p.get("code") for p in ((item.get("associations") or {}).get("featuremedia") or {}).get("products")
        ]

        # Check if the one of the companies products that has a superdesk product id matches one of the
        # image product id's
        sd_products = [p.get("sd_product_id") for p in products if p.get("sd_product_id")]

        return True if len(set(im_products) & set(sd_products)) else False
    else:
        return True


def get_company_from_newsapi_request(request: Request) -> CompanyResource:
    company = request.storage.request.get("company_instance")
    if company is None or (company and not company.is_enabled):
        raise AuthorizationError(403, gettext("Company not found or not enabled."))

    return company
