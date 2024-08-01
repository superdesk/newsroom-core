from copy import deepcopy

from flask_babel import gettext

from superdesk.flask import abort, request
from superdesk import get_resource_service
from superdesk.utc import utc_to_local

from newsroom.wire.search import items_query
from newsroom.agenda.agenda import get_date_filters
from newsroom.utils import query_resource, MAX_TERMS_SIZE


CHUNK_SIZE = 100


def get_items(args):
    """Get all the news items for the date and filters provided

    For performance reasons, returns an iterator that yields an array of CHUNK_SIZE
    So that aggregations can be queried while the next iteration is retrieved
    """

    if not args.get("section"):
        abort(400, gettext("Must provide a section for this report"))

    source = {
        "query": items_query(True),
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
    }

    must_terms = []
    if args.get("genre"):
        must_terms.append({"terms": {"genre.code": [genre for genre in args["genre"]]}})

    args["date_to"] = args["date_from"]
    date_range = get_date_filters(args)
    if date_range.get("gt") or date_range.get("lt"):
        must_terms.append({"range": {"versioncreated": date_range}})

    if len(must_terms) > 0:
        source["query"]["bool"]["filter"] += must_terms

    # Apply the section filters
    section = args["section"]
    get_resource_service("section_filters").apply_section_filter(source["query"], section)

    while True:
        results = get_resource_service(section if section == "agenda" else f"{section}_search").search(source)
        items = list(results)

        if not len(items):
            break

        source["from"] += CHUNK_SIZE

        yield items


def get_aggregations(args, ids):
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

    results = get_resource_service("history").fetch_history(source)
    aggs = (results.get("hits") or {}).get("aggregations") or {}
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


def get_facets(args):
    """Get aggregations for genre and companies using the date range and section

    This is used to populate the dropdown filters in the front-end
    """

    args["date_to"] = args["date_from"]
    date_range = get_date_filters(args)

    def get_genres():
        """Get the list of genres from the news items"""

        query = items_query(True)
        must_terms = []
        source = {}

        if date_range.get("gt") or date_range.get("lt"):
            must_terms.append({"range": {"versioncreated": date_range}})

        if len(must_terms) > 0:
            query["bool"]["filter"] += must_terms

        source.update(
            {
                "query": query,
                "size": 0,
                "aggs": {"genres": {"terms": {"field": "genre.code", "size": MAX_TERMS_SIZE}}},
            }
        )

        # Apply the section filters
        section = args["section"]
        get_resource_service("section_filters").apply_section_filter(source["query"], section)

        results = get_resource_service(section if section == "agenda" else f"{section}_search").search(source)

        buckets = ((results.hits.get("aggregations") or {}).get("genres") or {}).get("buckets") or []

        return [genre["key"] for genre in buckets]

    def get_companies():
        """Get the list of companies from the action history"""

        must_terms = [{"term": {"section": args["section"]}}]
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

    return {"genres": get_genres(), "companies": get_companies()}


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

    return rows


def get_content_activity_report():
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
        return get_facets(args)

    response = {"results": [], "name": gettext("Content activity")}

    for items in get_items(args):
        item_ids = [item.get("_id") for item in items]
        aggs = get_aggregations(args, item_ids)

        for item in items:
            item_id = item["_id"]

            if aggs.get(item_id):
                item["aggs"] = aggs[item_id]
            else:
                item["aggs"] = {"total": 0, "actions": {}, "companies": []}

            response["results"].append(item)

    return export_csv(args, response["results"]) if args.get("export") else response
