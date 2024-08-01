from superdesk import get_resource_service
from superdesk.core import get_app_config
from superdesk.utc import utcnow
from superdesk.flask import request, g


def post_api_audit(doc):
    audit_doc = {
        "created": utcnow(),
        "items_id": [doc.get("_id")] if doc.get("_id") else [i.get("_id") for i in doc.get("_items", [])],
        "remote_addr": request.access_route[0] if request.access_route else request.remote_addr,
        "uri": request.url,
        "endpoint": (request.endpoint or "").replace("|resource", ""),
    }

    # g.company_id is set via CompanyTokenAuth.check_auth]
    if "company_id" in g:
        audit_doc["subscriber"] = g.company_id

    get_resource_service("api_audit").post([audit_doc])


def format_report_results(search_result, unique_endpoints, companies):
    aggs = (search_result.hits or {}).get("aggregations") or {}
    buckets = (aggs.get("items") or {}).get("buckets") or []
    results = {}

    for b in buckets:
        company_name = (companies[b["key"]] or {}).get("name")
        results[company_name] = {}
        for endpoint_bucket in (b.get("endpoints") or {}).get("buckets") or []:
            results[company_name][endpoint_bucket["key"]] = endpoint_bucket["doc_count"]
            if endpoint_bucket["key"] not in unique_endpoints:
                unique_endpoints.append(endpoint_bucket["key"])

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
