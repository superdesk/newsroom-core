from typing import Any

from pydantic import Field, AliasChoices

from superdesk.core import get_app_config
from newsroom.search.types import NewshubSearchRequest, BaseSearchRequestArgs, SectionEnum, SearchFilterFunction
from newsroom.search.config import is_search_field_nested
from newsroom.search.filters import (
    get_apply_time_limit_filter,
    get_apply_filters,
    get_apply_highlights,
    apply_query_string,
    apply_ids_filter,
    apply_date_range,
    apply_advanced_search,
    prefill_user,
    prefill_company,
    prefill_products,
    prefill_args_from_topic,
    apply_section_filter,
    apply_company_filter,
    apply_products_filter,
    validate_request,
)
from newsroom.search.utils import query_string_for_section
from newsroom.settings import get_setting

from .types import DateRangeQuery, TimeFilter


class WireSearchRequestArgs(BaseSearchRequestArgs):
    """Search arguments for wire items"""

    #: If ``True``, will allow searching previous versions of an article
    ignore_latest: bool = Field(validation_alias=AliasChoices("ignore_latest", "ignoreLatest"), default=False)

    #: If ``True``, will exclude embargoed items from this search
    exclude_embargoed: bool = False

    #: If ``True``, will only include embargoed items in this search
    embargoed_only: bool = False

    #: If ``True``, will apply the configured NewsOnly filter for this search
    news_only: bool = Field(validation_alias=AliasChoices("news_only", "newsOnly"), default=False)

    #: An optional date_filter, from the list of configured date filters
    date_filter: str | None = None

    #: If ``True``, will include all versions in the response
    all_versions: bool = False

    #: If ``True``, will prepend embargoed items to the beginning of list of items in the response
    prepend_embargoed: bool = False

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        if self.prepend_embargoed:
            # Exclude embargoed items if we're prepending them anyway
            self.exclude_embargoed = True
            self.embargoed_only = False


def apply_embargoed_filters(request: NewshubSearchRequest) -> None:
    """Applies item embargo filter based on the request args"""

    embargo_query_rounding = get_app_config("EMBARGO_QUERY_ROUNDING")
    if request.args.exclude_embargoed:
        request.search.query.must_not.append({"range": {"embargoed": {"gt": f"now{embargo_query_rounding}"}}})
    elif request.args.embargoed_only:
        request.search.query.filter.append({"range": {"embargoed": {"gt": f"now{embargo_query_rounding}"}}})


def apply_news_only_filter(request: NewshubSearchRequest) -> None:
    """Applies news only filter based on the request args"""

    if not request.args.news_only or request.args.navigation_ids:
        return

    news_only_filter = get_setting("news_only_filter")
    if news_only_filter:
        request.search.query.must_not.append(
            query_string_for_section(request.section or SectionEnum.WIRE, news_only_filter)
        )
    else:
        request.search.query.must_not.extend(get_app_config("NEWS_ONLY_FILTERS") or [])


def apply_item_type_filter(request: NewshubSearchRequest) -> None:
    """Applies item type filter(s) based on the request args"""

    request.search.query.must_not.append({"term": {"type": "composite"}})
    if not request.args.ignore_latest:
        request.search.query.must_not.append({"constant_score": {"filter": {"exists": {"field": "nextversion"}}}})


def apply_bookmarks_query(request: NewshubSearchRequest) -> None:
    """Applies user bookmark filter based on the request args"""

    if not len(request.args.bookmarks):
        return

    request.search.query.filter.append({"terms": {"bookmarks": [str(user_id) for user_id in request.args.bookmarks]}})


def apply_date_filters(request: NewshubSearchRequest[WireSearchRequestArgs]) -> None:
    """Applies Wire date filter(s) based on the request args"""

    date_filter = request.args.date_filter
    date_range_query: DateRangeQuery | None = None
    time_filters = get_app_config("WIRE_TIME_FILTERS", [])

    if date_filter and date_filter != "custom_date":
        for time_filter in time_filters:
            if time_filter["filter"] == date_filter:
                date_range_query = time_filter["query"].copy()
                break
    elif not date_filter:
        default_time_filter: TimeFilter | None = next(
            (time_filter for time_filter in time_filters if time_filter["default"]), None
        )
        if default_time_filter and not request.args.bookmarks:
            date_range_query = default_time_filter["query"].copy()

    if date_range_query:
        date_range_query.setdefault("time_zone", get_app_config("DEFAULT_TIMEZONE"))
        request.search.query.must.append({"range": {"versioncreated": date_range_query}})


def apply_not_canceled_filter(request: NewshubSearchRequest) -> None:
    """Applies not cancelled filter based on the request args"""

    request.search.query.must_not.append({"term": {"pubstatus": "canceled"}})


def _get_wire_aggregations() -> dict[str, Any]:
    """Get the list of configured aggregations for the Wire resource"""

    return get_app_config("WIRE_AGGS") or {}


def _get_aggregation_field(key: str) -> str:
    """Returns the aggregation field based on the key"""

    aggregations = _get_wire_aggregations()
    if key not in aggregations:
        return key
    elif is_search_field_nested("items", key):
        return aggregations[key]["aggs"][f"{key}_filtered"]["aggs"][key]["terms"]["field"]
    else:
        return aggregations[key]["terms"]["field"]


def apply_aggs(request: NewshubSearchRequest) -> None:
    """Adds elasticsearch aggregations to the query, based on the request args"""

    if request.args.page > 0 or not request.args.aggs or request.search.aggs:
        return

    request.search.aggs = _get_wire_aggregations()


apply_time_limit_filter = get_apply_time_limit_filter("wire_time_limit_days")
apply_filters = get_apply_filters(_get_aggregation_field)

#: Defaults filters for use when highlighting search results
apply_highlights = get_apply_highlights(
    [
        apply_query_string,
        apply_ids_filter,
        apply_filters,
        apply_date_range,
        apply_date_filters,
        apply_advanced_search,
    ]
)

#: Default filters to run for Wire searches
default_wire_filters: list[SearchFilterFunction] = [
    prefill_user,
    prefill_company,
    prefill_products,
    prefill_args_from_topic,
    apply_ids_filter,
    apply_date_range,
    apply_date_filters,
    apply_time_limit_filter,
    apply_embargoed_filters,
    apply_item_type_filter,
    apply_section_filter,
    apply_news_only_filter,
    apply_products_filter,
    apply_company_filter,
    apply_filters,
    apply_bookmarks_query,
    apply_query_string,
    apply_advanced_search,
    apply_highlights,
    apply_aggs,
    validate_request,
]
