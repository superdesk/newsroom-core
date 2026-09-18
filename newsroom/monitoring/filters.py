from quart_babel import gettext

from content_api.errors import BadParameterValueError

from newsroom.types import SectionEnum, MonitoringProfileResourceModel
from newsroom.products import get_products_by_company_async
from newsroom.search.types import NewshubSearchRequest, SearchFilterFunction
from newsroom.search.filters import prefill_user, prefill_products, apply_products_filter
from newsroom.search.utils import query_string
from newsroom.wire.filters import WireSearchRequestArgs, default_wire_filters, apply_highlights, validate_request

from .service import MonitoringProfileService


class MonitoringSearchRequestArgs(WireSearchRequestArgs):
    skip_user_validation: bool = False


def prefill_search_section(request: NewshubSearchRequest[MonitoringSearchRequestArgs]) -> None:
    """Set the request section to WIRE, as that's where the content is"""
    request.section = SectionEnum.WIRE


async def prefill_monitoring_user(request: NewshubSearchRequest[MonitoringSearchRequestArgs]) -> None:
    """Prefill the user from the current request details"""

    if request.args.skip_user_validation:
        request.user = None
        return

    await prefill_user(request)


async def prefill_monitoring_products(request: NewshubSearchRequest[MonitoringSearchRequestArgs]) -> None:
    """Prefill the available products based on the current user, company and section"""

    if not request.company:
        request.products = []
        return

    request.products = await get_products_by_company_async(
        request.company,
        request.args.navigation_ids,
        product_type=request.section,
    )


async def apply_monitoring_products_filter(request: NewshubSearchRequest[MonitoringSearchRequestArgs]) -> None:
    """Applies product filter(s) based on the list of products on the request instance"""

    monitoring_list: list[MonitoringProfileResourceModel] = []
    monitoring_service = MonitoringProfileService()

    if len(request.args.navigation_ids) > 0:
        monitoring_profile = await monitoring_service.find_by_id(request.args.navigation_ids[0])
        if not monitoring_profile:
            raise BadParameterValueError(gettext("Monitoring profile not found"))
        monitoring_list = [monitoring_profile]
    elif request.web_request:
        raise BadParameterValueError(gettext("No monitoring profile requested."))
    else:
        monitoring_list = [monitoring_profile async for monitoring_profile in monitoring_service.get_all()]

    if len(monitoring_list) < 1:
        return

    for mlist in monitoring_list:
        if mlist.query:
            request.search.query.should.append(query_string(mlist.query))

    if request.args.navigation_ids and monitoring_list[0].keywords and len(monitoring_list[0].keywords):
        highlight = request.search.query.highlight
        highlight.setdefault("fields", {})["body_html"] = {
            "number_of_fragments": 0,
            "highlight_query": {
                "query_string": {
                    "query": " ".join(monitoring_list[0].keywords),
                    "default_operator": "AND",
                    "lenient": True,
                },
            },
        }
        highlight.update(
            dict(
                pre_tags=["<span class='es-highlight'>"],
                post_tags=["</span>"],
                require_field_match=False,
            ),
        )


#: Replace Wire/Common filters with Monitoring specific ones
filter_replacements: dict[SearchFilterFunction, SearchFilterFunction] = {
    prefill_user: prefill_monitoring_user,
    prefill_products: prefill_monitoring_products,
    apply_products_filter: apply_monitoring_products_filter,
}

#: Default filters to run for Monitoring searches
default_monitoring_filters: list[SearchFilterFunction] = [prefill_search_section] + [
    filter_replacements.get(filter_function) or filter_function
    for filter_function in default_wire_filters
    if filter_function not in [apply_highlights, validate_request]
]
