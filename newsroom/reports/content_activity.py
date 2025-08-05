from typing import Any, cast, TypedDict
from copy import deepcopy

from quart_babel import gettext

from superdesk.core.resources.cursor import ElasticsearchResourceCursorAsync
from superdesk.flask import abort, request
from superdesk import get_resource_service
from superdesk.utc import utc_to_local

from newsroom.types import SectionEnum
from newsroom.search.types import BaseSearchRequestArgs, NewshubSearchRequest
from newsroom.search.filters import apply_section_filter
from newsroom.wire.filters import apply_item_type_filter as apply_wire_type_filter
from newsroom.wire import WireItemService
from newsroom.agenda.filters import get_date_filters, apply_item_type_filter as apply_agenda_type_filter
from newsroom.agenda import AgendaItemService
from newsroom.history_async import HistoryService

from newsroom.utils import query_resource, MAX_TERMS_SIZE


CHUNK_SIZE = 100


async def get_query_source(args: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    search_request = NewshubSearchRequest[BaseSearchRequestArgs](section=SectionEnum(args["section"]))
    query = search_request.search.query

    if args.get("genre"):
        query.filter.append({"terms": {"genre.code": [genre for genre in args["genre"]]}})

    await apply_section_filter(search_request)

    if args["section"] == SectionEnum.AGENDA:
        # Set ``featured`` to True, so we don't add filters for Event, Planning, Combined type filter
        search_request.args.featured = True
        apply_agenda_type_filter(search_request)
    else:
        apply_wire_type_filter(search_request)

    date_range = get_date_filters(
        BaseSearchRequestArgs(
            start_date=args["date_from"],
            end_date=args["date_from"],
            timezone_offset=args.get("timezone_offset"),
        )
    )
    if date_range.get("gt") or date_range.get("lt"):
        query.filter.append({"range": {"versioncreated": date_range}})

    return search_request.search.generate_query_dict(source)


async def get_items(args):
    """Get all the news items for the date and filters provided

    For performance reasons, returns an iterator that yields an array of CHUNK_SIZE
    So that aggregations can be queried while the next iteration is retrieved
    """

    if not args.get("section"):
        abort(400, gettext("Must provide a section for this report"))

    source = await get_query_source(
        args,
        {
            "size": CHUNK_SIZE,
            "from": 0,
            "sort": [{"versioncreated": "asc"}],
            "_source": [
                "_resource",
                "headline",
                "place",
                "subject",
                "service",
                "versioncreated",
                "anpa_take_key",
                "source",
            ],
        },
    )

    service = AgendaItemService() if args["section"] == SectionEnum.AGENDA else WireItemService()

    while True:
        cursor = await service.search(source)
        items = await cursor.to_list()

        if not len(items):
            break

        source["from"] += CHUNK_SIZE
        yield [item.to_dict() for item in items]


class ItemAggregation(TypedDict):
    total: int
    actions: dict[str, int]
    companies: list[str]


async def get_aggregations(args: dict[str, Any], ids: list[str]) -> dict[str, ItemAggregation]:
    """Get action and company aggregations for the items provided"""

    if not args.get("section"):
        abort(400, gettext("Must provide a section for this report"))

    must_terms = [{"terms": {"item": ids}}, {"term": {"section": args["section"]}}]

    if args.get("company"):
        must_terms.append({"term": {"company": args["company"]}})

    if args.get("action"):
        must_terms.append({"terms": {"action": args["action"]}})

    source = {
        "query": {"bool": {"filter": must_terms}},
        "size": 0,
        "from": 0,
        "aggs": {
            "items": {
                "terms": {"field": "item", "size": MAX_TERMS_SIZE},
                "aggs": {
                    "actions": {"terms": {"field": "action", "size": MAX_TERMS_SIZE}},
                    "companies": {"terms": {"field": "company", "size": MAX_TERMS_SIZE}},
                },
            }
        },
    }

    results = cast(ElasticsearchResourceCursorAsync, await HistoryService().search(source))
    aggs = (results.hits or {}).get("aggregations") or {}
    buckets = (aggs.get("items") or {}).get("buckets") or []

    return {
        item["key"]: {
            "total": item["doc_count"],
            "actions": {
                action["key"]: action["doc_count"] for action in (item.get("actions") or {}).get("buckets") or []
            },
            "companies": [company["key"] for company in (item.get("companies") or {}).get("buckets") or []],
        }
        for item in buckets
    }


async def get_facets(args):
    """Get aggregations for genre and companies using the date range and section

    This is used to populate the dropdown filters in the front-end
    """

    section = args["section"]
    date_range = get_date_filters(
        BaseSearchRequestArgs(
            start_date=args["date_from"],
            end_date=args["date_from"],
            timezone_offset=args.get("timezone_offset"),
        )
    )

    async def get_genres():
        """Get the list of genres from the news items"""

        source = await get_query_source(
            args,
            {
                "size": 0,
                "aggs": {"genres": {"terms": {"field": "genre.code", "size": MAX_TERMS_SIZE}}},
            },
        )

        service = AgendaItemService() if args["section"] == SectionEnum.AGENDA else WireItemService()
        results = cast(ElasticsearchResourceCursorAsync, await service.search(source))
        buckets = ((results.hits.get("aggregations") or {}).get("genres") or {}).get("buckets") or []

        return [genre["key"] for genre in buckets]

    def get_companies():
        """Get the list of companies from the action history"""

        must_terms = [{"term": {"section": section}}]
        if date_range.get("gt") or date_range.get("lt"):
            must_terms.append({"range": {"_created": date_range}})

        source = {
            "query": {"bool": {"filter": must_terms}},
            "size": 0,
            "from": 0,
            "aggs": {"companies": {"terms": {"field": "company", "size": MAX_TERMS_SIZE}}},
        }

        results = get_resource_service("history").fetch_history(source)
        aggs = (results.get("hits") or {}).get("aggregations") or {}
        buckets = (aggs.get("companies") or {}).get("buckets") or []

        return [company["key"] for company in buckets]

    return {"genres": await get_genres(), "companies": get_companies()}


def export_csv(args, results):
    """Generate 2-dimensional array for generating the CSV output"""

    companies = {str(company["_id"]): company for company in query_resource("companies")}

    rows = [
        [
            gettext("Published"),
            gettext("Headline"),
            gettext("Take Key"),
            gettext("Place"),
            gettext("Category"),
            gettext("Subject"),
            gettext("Source"),
            gettext("Companies"),
            gettext("Actions"),
        ]
    ]

    actions = args.get("action") or [
        "download",
        "copy",
        "share",
        "print",
        "open",
        "preview",
        "clipboard",
        "api",
    ]

    if "download" in actions:
        rows[0].append(gettext("Download"))

    if "copy" in actions:
        rows[0].append(gettext("Copy"))

    if "share" in actions:
        rows[0].append(gettext("Share"))

    if "print" in actions:
        rows[0].append(gettext("Print"))

    if "open" in actions:
        rows[0].append(gettext("Open"))

    if "preview" in actions:
        rows[0].append(gettext("Preview"))

    if "clipboard" in actions:
        rows[0].append(gettext("Clipboard"))

    if "api" in actions:
        rows[0].append(gettext("API retrieval"))

    for item in results:
        aggs = item.get("aggs") or {}

        row = [
            utc_to_local("Australia/Sydney", item.get("versioncreated")).strftime("%H:%M"),
            item.get("headline"),
            item.get("anpa_take_key") or "",
            "\r\n".join(sorted([place.get("name") or "" for place in item.get("place") or []])),
            "\r\n".join(sorted([service.get("name") or "" for service in item.get("service") or []])),
            "\r\n".join(sorted([subject.get("name") or "" for subject in item.get("subject") or []])),
            item.get("source", ""),
            "\r\n".join(
                sorted(
                    [
                        (companies.get(company_id) or {}).get("name") or company_id
                        for company_id in aggs.get("companies") or []
                    ]
                )
            ),
            aggs.get("total") or 0,
        ]

        action_names = ["download", "copy", "share", "print", "open", "preview", "clipboard", "api"]
        for action_name in action_names:
            if action_name in actions:
                row.append((aggs.get("actions") or {}).get(action_name, 0))

        rows.append(row)

    return rows


async def get_content_activity_report():
    """Entrypoint for generating the data for the ContentActivity report"""

    args = deepcopy(request.args.to_dict())

    if args.get("genre"):
        args["genre"] = args["genre"].split(",")

    if args.get("action"):
        args["action"] = args["action"].split(",")

    if not args.get("section"):
        args["section"] = "wire"

    if args.get("aggregations"):
        # This request is for populating the dropdown filters
        # for genre and companies
        return await get_facets(args)

    response = {"results": [], "name": gettext("Content activity")}

    async for items in get_items(args):
        item_ids = [item.get("_id") for item in items]
        aggs = await get_aggregations(args, item_ids)

        for item in items:
            item_id = item["_id"]

            if aggs.get(item_id):
                item["aggs"] = aggs[item_id]
            else:
                item["aggs"] = {"total": 0, "actions": {}, "companies": []}

            response["results"].append(item)

    return export_csv(args, response["results"]) if args.get("export") else response
