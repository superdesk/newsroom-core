from quart_babel import gettext

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


def get_company_from_newsapi_request(request: Request) -> CompanyResource:
    company = request.storage.request.get("company_instance")
    if company is None or (company and not company.is_enabled):
        raise AuthorizationError(403, gettext("Company not found or not enabled."))

    return company
