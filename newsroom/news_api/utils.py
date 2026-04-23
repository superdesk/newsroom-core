import re
from datetime import datetime

from quart_babel import gettext
from superdesk import get_app_config

from superdesk.core.types import Request
from superdesk.core.resources.cursor import ElasticsearchResourceCursorAsync
from superdesk.flask import request as flask_request

from newsroom.types import NewsApiAuditResourceModel, CompanyResource
from newsroom.exceptions import AuthorizationError
from logging import getLogger

logger = getLogger(__name__)


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


def format_api_date(date_string: str) -> str:
    """
    Converts an Elasticsearch 7.1+ high-precision date string
    to a legacy format.
    @param date_string:
    @return: formatted date string
    """

    if not date_string:
        return ""

    target_format = get_app_config("API_DATE_FORMAT")
    if target_format is None:
        return date_string

    # Standardize the timezone offset
    # ES 7.1 often uses +00:00, but Python's %z and older ES expect +0000
    # This regex removes the colon in the last 5 characters if it exists
    clean_date = re.sub(r"(\+\d{2}):(\d{2})$", r"\1\2", date_string)

    try:
        dt = datetime.strptime(clean_date, "%Y-%m-%dT%H:%M:%S%z")
        return dt.strftime(target_format)
    except ValueError as e:
        # Fallback if the string is weirdly formatted
        logger.warning(f"Error parsing date {date_string}: {e}")
        return date_string
