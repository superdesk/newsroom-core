from typing import Any, Annotated
from datetime import datetime
import re

from pydantic import field_validator, Field, AliasChoices

from superdesk.core import get_app_config, json
from superdesk.core.types import ESBoolQuery, SortListParam

from newsroom.types import AgendaItemType, SectionEnum
from newsroom.search.types import BaseSearchRequestArgs, SearchFilterFunction, NewshubSearchRequest, QueryStringQuery
from newsroom.search.utils import query_string, query_string_for_section, get_filter_query
from newsroom.search.config import is_search_field_nested, get_nested_config
from newsroom.utils import get_local_date, get_end_date
from newsroom.search.filters import (
    prefill_user,
    prefill_company,
    prefill_products,
    prefill_args_from_topic,
    apply_company_filter,
    apply_products_filter,
    apply_section_filter,
    apply_ids_filter,
    apply_advanced_search,
    get_apply_highlights,
)

""""
company_filter
products filters
product planning filters
agenda items query
section filter
apply_request_filter

if not is_admin_or_internal:
    remove_fields(PRIVATE_FIELDS)

itemType param filters (events / planning / get_app_config("AGENDA_DEFAULT_FILTER_HIDE_PLANNING") / default)

custom agenda filters:
    q
    id/ids
    bookmarks
    dates
    filters
    advanced

"""

PRIVATE_FIELDS = ["event.files", "*.internal_note"]
PLANNING_ITEMS_FIELDS = ["planning_items", "coverages", "display_dates"]

aggregations: dict[str, dict[str, Any]] = {
    "language": {"terms": {"field": "language"}},
    "calendar": {"terms": {"field": "calendars.name", "size": 100}},
    "service": {"terms": {"field": "service.name", "size": 100}},
    "subject": {"terms": {"field": "subject.name", "size": 200}},
    "urgency": {"terms": {"field": "urgency"}},
    "place": {"terms": {"field": "place.name", "size": 50}},
    "coverage": {
        "nested": {"path": "coverages"},
        "aggs": {"coverage_type": {"terms": {"field": "coverages.coverage_type", "size": 10}}},
    },
    "planning_items": {
        "nested": {
            "path": "planning_items",
        },
        "aggs": {
            "service": {"terms": {"field": "planning_items.service.name", "size": 100}},
            "subject": {"terms": {"field": "planning_items.subject.name", "size": 200}},
            "urgency": {"terms": {"field": "planning_items.urgency"}},
            "place": {"terms": {"field": "planning_items.place.name", "size": 50}},
        },
    },
    "agendas": {
        "nested": {"path": "planning_items"},
        "aggs": {
            "agenda": {"terms": {"field": "planning_items.agendas.name", "size": 100}},
        },
    },
}


class AgendaSearchRequestArgs(BaseSearchRequestArgs):
    #: The sorting that should be applied to this request
    sort: SortListParam = [("dates.start", 1)]

    item_type: Annotated[AgendaItemType | None, Field(validation_alias=AliasChoices("item_type", "itemType"))] = None
    featured: bool = False

    @field_validator("item_type", mode="before")
    def parse_item_type(cls, value: str) -> str:
        # Make sure that we use the same value type for item type and search item type
        return "event" if value == "events" else value


def get_date_filters(args: BaseSearchRequestArgs):
    date_range = {}
    offset = args.timezone_offset or 0
    if args.start_date:
        date_range["gt"] = get_local_date(args.start_date, args.start_time, offset)
    if args.end_date:
        date_range["lt"] = get_end_date(args.end_date, get_local_date(args.end_date, args.end_time, offset))

    return date_range


def prefill_item_type_arg(request: NewshubSearchRequest[AgendaSearchRequestArgs]) -> None:
    if request.user and not request.user.is_admin() and request.company and request.company.events_only:
        request.args.item_type = AgendaItemType.EVENT


def apply_item_state_filter(request: NewshubSearchRequest[AgendaSearchRequestArgs]) -> None:
    request.search.query.must_not.append({"term": {"state": "killed"}})

    if request.user and not request.user.is_admin_or_internal():
        request.search.exclude_fields.extend(PRIVATE_FIELDS)


def apply_item_type_filter(request: NewshubSearchRequest[AgendaSearchRequestArgs]) -> None:
    item_type = request.args.item_type
    if item_type == AgendaItemType.EVENT:
        # no adhoc planning items and remove planning items and coverages fields
        request.search.query.filter.append(
            {
                "bool": {
                    "should": [
                        {"term": {"item_type": "event"}},
                        {
                            # Match Events before ``item_type`` field was added
                            "bool": {
                                "must_not": [{"exists": {"field": "item_type"}}],
                                "filter": [{"exists": {"field": "event_id"}}],
                            },
                        },
                    ],
                    "minimum_should_match": 1,
                },
            }
        )
        request.search.exclude_fields.extend(PLANNING_ITEMS_FIELDS)
    elif item_type == AgendaItemType.PLANNING:
        request.search.query.filter.append(
            {
                "bool": {
                    "should": [
                        {"term": {"item_type": "planning"}},
                        {
                            # Match Planning before ``item_type`` field was added
                            "bool": {
                                "must_not": [
                                    {"exists": {"field": "item_type"}},
                                    {"exists": {"field": "event_id"}},
                                ],
                            },
                        },
                    ],
                    "minimum_should_match": 1,
                }
            }
        )
    elif get_app_config("AGENDA_DEFAULT_FILTER_HIDE_PLANNING"):
        request.search.query.filter.append(
            {
                "bool": {
                    "should": [
                        {"term": {"item_type": "event"}},
                        {
                            # Match Events before ``item_type`` field was added
                            "bool": {
                                "must_not": [{"exists": {"field": "item_type"}}],
                                "filter": [{"exists": {"field": "event_id"}}],
                            },
                        },
                    ],
                    "minimum_should_match": 1,
                },
            }
        )
        request.search.exclude_fields.extend(["planning_items", "display_dates"])
    else:
        # Don't include Planning items that are associated with an Event
        request.search.query.filter.append(
            {
                "bool": {
                    "should": [
                        {"bool": {"must_not": [{"exists": {"field": "item_type"}}]}},
                        {"term": {"item_type": "event"}},
                        {
                            "bool": {
                                "filter": [{"term": {"item_type": "planning"}}],
                                "must_not": [{"exists": {"field": "event_id"}}],
                            },
                        },
                    ],
                    "minimum_should_match": 1,
                },
            }
        )


def planning_items_query_string(query: str, fields: list[str] | None = None, nested: bool = False) -> QueryStringQuery:
    if nested:
        # when searching nested planning items we need to prefix field names
        # in query with `planning_items.` otherwise it will never match in nested
        # field and negative queries eg. NOT service.name:Sport will match all
        # nested planning items
        query = re.sub(
            r"""\b(
                service\.name|
                service\.code|
                subject\.name|
                subject\.code|
                headline|
                slugline|
                description_text|
                guid
            ):""",
            r"planning_items.\1:",
            query,
            flags=re.VERBOSE,
        )

    return query_string(query, fields=fields or ["planning_items.*"])


def nested_query(path, query, inner_hits=True, name=None):
    nested = {"path": path, "query": query}
    if inner_hits:
        nested["inner_hits"] = {}
        if name:
            nested["inner_hits"]["name"] = name

    return {"nested": nested}


def apply_product_planning_filters(request: NewshubSearchRequest[AgendaSearchRequestArgs]) -> None:
    planning_items_should = []
    for product in request.products:
        if product.planning_item_query and request.args.item_type != AgendaItemType.EVENT:
            planning_items_should.append(planning_items_query_string(product.planning_item_query))

    if len(planning_items_should):
        request.search.query.should.append(
            nested_query(
                "planning_items",
                {
                    "bool": {
                        "should": planning_items_should,
                        "minimum_should_match": 1,
                    },
                },
                name="products",
            )
        )


def apply_agenda_query_string(request: NewshubSearchRequest[AgendaSearchRequestArgs]) -> None:
    if not request.args.q:
        return

    q_dict: dict[str, Any] | None = None
    try:
        q_dict = json.loads(request.args.q)
    except ValueError:
        pass

    if q_dict is None:
        # Normal query string query
        query = query_string_for_section(SectionEnum.AGENDA, request.args.q)
        if request.args.item_type == AgendaItemType.EVENT:
            # Events Only
            request.search.query.filter.append(query)
        else:
            request.search.query.filter.append(
                {
                    "bool": {
                        "should": [
                            query,
                            nested_query(
                                "planning_items",
                                planning_items_query_string(request.args.q, nested=True),
                                name="query",
                            ),
                        ],
                        "minimum_should_match": 1,
                    },
                }
            )
    else:
        # Complex Agenda query string
        filters: list[dict[str, Any] | QueryStringQuery] = []
        if q_dict.get("query"):
            filters.append(query_string_for_section(SectionEnum.AGENDA, q_dict["query"]))

        if q_dict.get("planning_item_query"):
            filters.append(
                nested_query(
                    "planning_items",
                    planning_items_query_string(q_dict["planning_item_query"]),
                    name="product_test",
                ),
            )

        if len(filters):
            request.search.query.filter.append(
                {
                    "bool": {
                        "should": filters,
                        "minimum_should_match": 1,
                    }
                }
            )


def apply_agenda_bookmarks_query(request: NewshubSearchRequest[AgendaSearchRequestArgs]) -> None:
    if not len(request.args.bookmarks):
        return

    user_ids: list[str] = [str(user_id) for user_id in request.args.bookmarks]
    request.search.query.filter.append(
        {
            "bool": {
                "should": [
                    {"terms": {"bookmarks": user_ids}},
                    {"terms": {"watches": user_ids}},
                    {
                        "nested": {
                            "path": "coverages",
                            "query": {"bool": {"should": [{"terms": {"coverages.watches": user_ids}}]}},
                        }
                    },
                ],
            },
        }
    )


def gen_date_range_filter(field: str, operator: str, date_str: str, datetime_instance: datetime):
    return [
        {
            "bool": {
                "must_not": {"term": {"dates.all_day": True}},
                "filter": {"range": {field: {operator: datetime_instance}}},
            },
        },
        {
            "bool": {
                "filter": [
                    {"term": {"dates.all_day": True}},
                    {"range": {field: {operator: date_str}}},
                ],
            },
        },
    ]


def apply_agenda_date_filters(request: NewshubSearchRequest[AgendaSearchRequestArgs]) -> None:
    date_range = get_date_filters(request.args)
    date_from = date_range.get("gt")
    date_to = date_range.get("lt")
    should = []

    if request.args.start_date and date_from and not date_to:
        # Filter from a particular date onwards
        should = gen_date_range_filter("dates.end", "gte", request.args.start_date, date_from)
    elif request.args.end_date and not date_from and date_to:
        # Filter up to a particular date
        should = gen_date_range_filter("dates.end", "lte", request.args.end_date, date_to)
    elif request.args.start_date and request.args.end_date and date_from and date_to:
        # Filter based on the date range provided
        should = [
            {
                # Both start/end dates are inside the range
                "bool": {
                    "filter": [
                        {"range": {"dates.start": {"gte": date_from}}},
                        {"range": {"dates.end": {"lte": date_to}}},
                    ],
                    "must_not": {"term": {"dates.all_day": True}},
                },
            },
            {
                # Both start/end dates are inside the range, all day version
                "bool": {
                    "filter": [
                        {"range": {"dates.start": {"gte": request.args.start_date}}},
                        {"range": {"dates.end": {"lte": request.args.end_date}}},
                        {"term": {"dates.all_day": True}},
                    ],
                },
            },
            {
                # Starts before date_from and finishes after date_to
                "bool": {
                    "filter": [
                        {"range": {"dates.start": {"lt": date_from}}},
                        {"range": {"dates.end": {"gt": date_to}}},
                    ],
                    "must_not": {"term": {"dates.all_day": True}},
                },
            },
            {
                # Starts before date_from and finishes after date_to, all day version
                "bool": {
                    "filter": [
                        {"range": {"dates.start": {"lt": request.args.start_date}}},
                        {"range": {"dates.end": {"gt": request.args.end_date}}},
                        {"term": {"dates.all_day": True}},
                    ],
                },
            },
            {
                # Start date is within range OR End date is within range
                "bool": {
                    "should": [
                        {"range": {"dates.start": {"gte": date_from, "lte": date_to}}},
                        {"range": {"dates.end": {"gte": date_from, "lte": date_to}}},
                    ],
                    "must_not": {"term": {"dates.all_day": True}},
                    "minimum_should_match": 1,
                },
            },
            {
                # Start date is within range OR End date is within range, all day version
                "bool": {
                    "should": [
                        {"range": {"dates.start": {"gte": request.args.start_date, "lte": request.args.end_date}}},
                        {"range": {"dates.end": {"gte": request.args.start_date, "lte": request.args.end_date}}},
                    ],
                    "filter": {"term": {"dates.all_day": True}},
                    "minimum_should_match": 1,
                },
            },
        ]

    if date_range:
        # Get events for extra dates for coverages and planning.
        should.append({"range": {"display_dates.date": date_range}})

    if len(should):
        request.search.query.filter.append({"bool": {"should": should, "minimum_should_match": 1}})


coverage_filters = ["coverage", "coverage_status"]
planning_filters = coverage_filters + ["agendas"]


def get_aggregation_field(key: str):
    if key == "coverage":
        return aggregations[key]["aggs"]["coverage_type"]["terms"]["field"]
    elif key == "agendas":
        return aggregations[key]["aggs"]["agenda"]["terms"]["field"]
    elif is_search_field_nested("agenda", key):
        return aggregations[key]["aggs"][f"{key}_filtered"]["aggs"][key]["terms"]["field"]
    return aggregations[key]["terms"]["field"]


def apply_location_filter(query: ESBoolQuery, val: dict[str, Any]) -> None:
    search_type = val.get("type", "location")

    if search_type == "city":
        field = "location.address.city.keyword"
    elif search_type == "state":
        field = "location.address.state.keyword"
    elif search_type == "country":
        field = "location.address.country.keyword"
    else:
        field = "location.name.keyword"

    query.filter.append({"term": {field: val.get("name")}})


def apply_coverage_filter(query: ESBoolQuery, val: dict[str, Any]) -> None:
    query.filter.append(
        nested_query(
            path="coverages",
            query={"terms": {get_aggregation_field("coverage"): val}},
            name="coverage",
        )
    )


def apply_coverage_status_filter(query: ESBoolQuery, val: list[str]) -> None:
    if val == ["planned"]:
        query.filter.append(
            nested_query(
                path="coverages",
                query={"terms": {"coverages.coverage_status": ["coverage intended"]}},
                name="coverage_status",
            )
        )
        query.must_not.extend(
            [
                nested_query(
                    path="coverages",
                    query={"exists": {"field": "coverages.delivery_id"}},
                ),
                nested_query(
                    path="coverages",
                    query={"terms": {"coverages.workflow_status": ["completed"]}},
                    name="workflow_status",
                ),
            ]
        )
    elif val == ["may be"]:
        query.filter.append(
            nested_query(
                path="coverages",
                query={
                    "terms": {
                        "coverages.coverage_status": [
                            "coverage not decided yet",
                            "coverage upon request",
                        ],
                    },
                },
                name="coverage_status",
            )
        )
    elif val == ["not planned"]:
        query.must_not.append(
            nested_query(
                path="coverages",
                query={"exists": {"field": "coverages"}},
                name="coverage_status",
            )
        )
    elif val == ["completed"]:
        should_term_filters = []
        # Check if "delivery_id" is present
        should_term_filters.append(
            nested_query(
                path="coverages",
                query={"exists": {"field": "coverages.delivery_id"}},
            )
        )

        # If "delivery_id" is not present, check "workflow_status"
        should_term_filters.append(
            nested_query(
                path="coverages",
                query={"terms": {"coverages.workflow_status": ["completed"]}},
                name="workflow_status",
            )
        )
        query.filter.append(
            {
                "bool": {
                    "should": should_term_filters,
                    "minimum_should_match": 1,
                },
            }
        )
    elif val == ["not intended"]:
        query.filter.append(
            nested_query(
                path="coverages",
                query={"terms": {"coverages.coverage_status": ["coverage not intended"]}},
                name="coverage_status",
            )
        )


def apply_agendas_filter(query: ESBoolQuery, val) -> None:
    query.filter.append(
        nested_query(
            path="planning_items",
            query={"terms": {get_aggregation_field("agendas"): val}},
            name="agendas",
        )
    )


def get_apply_agenda_filters(highlights: bool) -> SearchFilterFunction:
    def _apply_agenda_filters(request: NewshubSearchRequest[AgendaSearchRequestArgs]) -> None:
        if not request.args.filter:
            return

        query = request.search.post_filter if get_app_config("FILTER_BY_POST_FILTER", False) else request.search.query

        for key, val in request.args.filter.items():
            is_event_type = request.args.item_type == AgendaItemType.EVENT
            if not val or (is_event_type and key in planning_filters):
                continue

            match key:
                case "location":
                    apply_location_filter(query, val)
                case "coverage":
                    apply_coverage_filter(query, val)
                case "coverage_status":
                    apply_coverage_status_filter(query, val)
                case "agendas":
                    apply_agendas_filter(query, val)
                case _:
                    agg_field = get_aggregation_field(key)
                    filter_query = get_filter_query(key, val, agg_field, get_nested_config("agenda", key))
                    if not is_event_type:
                        query.filter.append(
                            {
                                "bool": {
                                    "minimum_should_match": 1,
                                    "should": [
                                        filter_query,
                                        nested_query(
                                            path="planning_items",
                                            query={
                                                "bool": {"filter": [{"terms": {f"planning_items.{agg_field}": val}}]}
                                            },
                                            name=key,
                                            inner_hits=highlights,
                                        ),
                                    ],
                                },
                            }
                        )
                    else:
                        query.filter.append(filter_query)

    return _apply_agenda_filters


apply_agenda_filters = get_apply_agenda_filters(False)
apply_agenda_highlights_filters = get_apply_agenda_filters(True)

apply_highlights = get_apply_highlights(
    [
        apply_agenda_query_string,
        apply_ids_filter,
        apply_agenda_highlights_filters,
        apply_agenda_date_filters,
        apply_advanced_search,
    ]
)

filters_without_dates: list[SearchFilterFunction] = [
    apply_item_state_filter,
    apply_item_type_filter,
    apply_section_filter,
    apply_company_filter,
    apply_products_filter,
    apply_product_planning_filters,
    apply_ids_filter,
    apply_agenda_query_string,
    apply_agenda_bookmarks_query,
    apply_advanced_search,
    apply_agenda_filters,
]

#: Default filters to run for Agenda searches
default_agenda_filters: list[SearchFilterFunction] = [
    # Prefill request variables
    prefill_user,
    prefill_company,
    prefill_products,
    prefill_args_from_topic,
    prefill_item_type_arg,
    apply_agenda_date_filters,
] + filters_without_dates
