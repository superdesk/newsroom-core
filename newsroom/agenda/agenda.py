from typing import Dict, Set, Any, Optional
import logging
from copy import deepcopy

from bson import ObjectId
from content_api.items.resource import code_mapping
from eve.utils import ParsedRequest, config
from flask import json, abort, current_app as app
from flask_babel import lazy_gettext

from planning.common import (
    WORKFLOW_STATE_SCHEMA,
    ASSIGNMENT_WORKFLOW_STATE,
    WORKFLOW_STATE,
)
from planning.events.events_schema import events_schema
from planning.planning.planning import planning_schema
from superdesk import get_resource_service
from superdesk.resource import Resource, not_enabled, not_analyzed, not_indexed
from superdesk.utils import ListCursor
from superdesk.metadata.item import metadata_schema

import newsroom
from newsroom.agenda.email import (
    send_coverage_notification_email,
    send_agenda_notification_email,
)
from newsroom.auth import get_company, get_user
from newsroom.notifications import (
    save_user_notifications,
    UserNotification,
)
from newsroom.template_filters import is_admin_or_internal, is_admin
from newsroom.utils import (
    get_user_dict,
    get_company_dict,
    get_entity_or_404,
    parse_date_str,
)
from newsroom.utils import get_local_date, get_end_date
from datetime import datetime
from newsroom.wire import url_for_wire
from newsroom.search.service import BaseSearchService, SearchQuery, query_string, get_filter_query
from newsroom.search.config import is_search_field_nested, get_nested_config
from .utils import get_latest_available_delivery, TO_BE_CONFIRMED_FIELD, push_agenda_item_notification


logger = logging.getLogger(__name__)
PRIVATE_FIELDS = ["event.files", "*.internal_note"]
PLANNING_ITEMS_FIELDS = ["planning_items", "coverages", "display_dates"]


agenda_notifications = {
    "event_updated": {
        "message": lazy_gettext("An event you have been watching has been updated"),
        "subject": lazy_gettext("Event updated"),
    },
    "event_unposted": {
        "message": lazy_gettext("An event you have been watching has been cancelled"),
        "subject": lazy_gettext("Event cancelled"),
    },
    "planning_added": {
        "message": lazy_gettext("An event you have been watching has a new planning"),
        "subject": lazy_gettext("Planning added"),
    },
    "planning_cancelled": {
        "message": lazy_gettext("An event you have been watching has a planning cancelled"),
        "subject": lazy_gettext("Planning cancelled"),
    },
    "coverage_added": {
        "message": lazy_gettext("An event you have been watching has a new coverage added"),
        "subject": lazy_gettext("Coverage added"),
    },
}

nested_code_mapping = {
    "type": "list",
    "mapping": {
        "type": "nested",
        "include_in_parent": True,
        "properties": code_mapping["properties"],
    },
}


def set_saved_items_query(query, user_id):
    query["bool"]["filter"].append(
        {
            "bool": {
                "should": [
                    {"term": {"bookmarks": str(user_id)}},
                    {"term": {"watches": str(user_id)}},
                    {
                        "nested": {
                            "path": "coverages",
                            "query": {"bool": {"should": [{"term": {"coverages.watches": str(user_id)}}]}},
                        }
                    },
                ],
            },
        }
    )


class AgendaResource(newsroom.Resource):
    """
    Agenda schema
    """

    SUPPORTED_NESTED_SEARCH_FIELDS = ["subject"]

    schema = {}

    # identifiers
    schema["guid"] = events_schema["guid"]
    schema["type"] = {
        "type": "string",
        "mapping": not_analyzed,
        "default": "agenda",
    }
    schema["event_id"] = events_schema["guid"]
    schema["item_type"] = {
        "type": "string",
        "mapping": not_analyzed,
        "nullable": False,
        "allowed": ["event", "planning"],
    }
    schema["recurrence_id"] = {
        "type": "string",
        "mapping": not_analyzed,
        "nullable": True,
    }

    # content metadata
    schema["name"] = metadata_schema["body_html"].copy()
    schema["slugline"] = not_analyzed
    schema["definition_short"] = metadata_schema["body_html"].copy()
    schema["definition_long"] = metadata_schema["body_html"].copy()
    schema["headline"] = metadata_schema["body_html"].copy()
    schema["firstcreated"] = events_schema["firstcreated"]
    schema["version"] = events_schema["version"]
    schema["versioncreated"] = events_schema["versioncreated"]
    schema["ednote"] = events_schema["ednote"]
    schema["registration_details"] = {"type": "string"}
    schema["invitation_details"] = {"type": "string"}
    schema["language"] = {"type": "string", "mapping": {"type": "keyword"}}
    schema["source"] = {"type": "string", "mapping": {"type": "keyword"}}

    # aggregated fields
    schema["urgency"] = planning_schema["urgency"]
    schema["place"] = planning_schema["place"]
    schema["service"] = planning_schema["anpa_category"]
    schema["state_reason"] = {"type": "string"}

    # Fields supporting Nested Aggregation / Filtering
    schema["subject"] = nested_code_mapping

    # dates
    schema["dates"] = {
        "type": "dict",
        "schema": {
            "start": {"type": "datetime"},
            "end": {"type": "datetime"},
            "tz": {"type": "string"},
        },
    }

    # additional dates from coverages or planning to be used in searching agenda items
    schema["display_dates"] = {
        "type": "list",
        "nullable": True,
        "schema": {
            "type": "dict",
            "schema": {
                "date": {"type": "datetime"},
            },
        },
    }

    # coverages
    schema["coverages"] = {
        "type": "list",
        "mapping": {
            "type": "nested",
            "properties": {
                "planning_id": not_analyzed,
                "coverage_id": not_analyzed,
                "scheduled": {"type": "date"},
                "coverage_type": not_analyzed,
                "workflow_status": not_analyzed,
                "coverage_status": not_analyzed,
                "coverage_provider": not_analyzed,
                "slugline": not_analyzed,
                "delivery_id": not_analyzed,  # To point ot the latest published item
                "delivery_href": not_analyzed,  # To point ot the latest published item
                TO_BE_CONFIRMED_FIELD: {"type": "boolean"},
                "deliveries": {  # All deliveries (incl. updates go here)
                    "type": "object",
                    "properties": {
                        "planning_id": not_analyzed,
                        "coverage_id": not_analyzed,
                        "assignment_id": not_analyzed,
                        "sequence_no": not_analyzed,
                        "publish_time": {"type": "date"},
                        "delivery_id": not_analyzed,
                        "delivery_state": not_analyzed,
                    },
                },
                "watches": not_analyzed,
            },
        },
    }

    # attachments
    schema["files"] = {
        "type": "list",
        "mapping": not_enabled,
    }

    # state
    schema["state"] = WORKFLOW_STATE_SCHEMA

    # other searchable fields needed in UI
    schema["calendars"] = events_schema["calendars"]
    schema["location"] = events_schema["location"]

    # update location name to allow exact search and term based searching
    schema["location"]["mapping"]["properties"]["name"] = {"type": "text", "fields": {"keyword": {"type": "keyword"}}}

    # event details
    schema["event"] = {
        "type": "dict",
        "mapping": not_enabled,
    }

    # planning details which can be more than one per event
    schema["planning_items"] = {
        "type": "list",
        "mapping": {
            "type": "nested",
            "include_in_all": False,
            "properties": {
                "_id": not_analyzed,
                "guid": not_analyzed,
                "slugline": not_analyzed,
                "description_text": {"type": "string"},
                "headline": {"type": "string"},
                "abstract": {"type": "string"},
                "subject": nested_code_mapping["mapping"],
                "urgency": {"type": "integer"},
                "service": code_mapping,
                "planning_date": {"type": "date"},
                "coverages": not_enabled,
                "agendas": {
                    "type": "object",
                    "properties": {
                        "name": not_analyzed,
                        "_id": not_analyzed,
                    },
                },
                "ednote": {"type": "string"},
                "internal_note": not_indexed,
                "place": planning_schema["place"]["mapping"],
                "state": not_analyzed,
                "state_reason": {"type": "string"},
                "products": {
                    "type": "object",
                    "properties": {"code": not_analyzed, "name": not_analyzed},
                },
            },
        },
    }

    schema["bookmarks"] = Resource.not_analyzed_field("list")  # list of user ids who bookmarked this item
    schema["downloads"] = Resource.not_analyzed_field("list")  # list of user ids who downloaded this item
    schema["shares"] = Resource.not_analyzed_field("list")  # list of user ids who shared this item
    schema["prints"] = Resource.not_analyzed_field("list")  # list of user ids who printed this item
    schema["copies"] = Resource.not_analyzed_field("list")  # list of user ids who copied this item
    schema["watches"] = Resource.not_analyzed_field("list")  # list of users following the event

    # matching products from superdesk
    schema["products"] = {
        "type": "list",
        "mapping": {
            "type": "object",
            "properties": {"code": not_analyzed, "name": not_analyzed},
        },
    }

    resource_methods = ["GET"]
    datasource = {
        "source": "agenda",
        "search_backend": "elastic",
        "default_sort": [("dates.start", 1)],
    }

    item_methods = ["GET"]


def _agenda_query():
    return {
        "bool": {
            "filter": [],
            "should": [],
            "must_not": [{"term": {"state": "killed"}}],
        }
    }


def get_date_filters(args):
    date_range = {}
    offset = int(args.get("timezone_offset", "0"))
    if args.get("date_from"):
        date_range["gt"] = get_local_date(args["date_from"], "00:00:00", offset)
    if args.get("date_to"):
        date_range["lt"] = get_end_date(args["date_to"], get_local_date(args["date_to"], "23:59:59", offset))
    return date_range


def _set_event_date_range(search):
    """Get events for selected date.

    ATM it should display everything not finished by that date, even starting later.

    :param newsroom.search.SearchQuery search: The search query instance
    """

    date_range = get_date_filters(search.args)
    date_from = date_range.get("gt")
    date_to = date_range.get("lt")

    should = []

    if date_from and not date_to:
        # Filter from a particular date onwards
        should = [
            {
                "bool": {
                    "filter": {"range": {"dates.start": {"gte": date_from}}},
                    "must_not": {"term": {"dates.all_day": True}},
                },
            },
            {
                "bool": {
                    "filter": [
                        {"term": {"dates.all_day": True}},
                        {"range": {"dates.start": {"gte": search.args["date_from"]}}},
                    ],
                },
            },
        ]
    elif not date_from and date_to:
        # Filter up to a particular date
        should = [
            {
                "bool": {
                    "filter": {"range": {"dates.end": {"lte": date_to}}},
                    "must_not": {"term": {"dates.all_day": True}},
                },
            },
            {
                "bool": {
                    "filter": [
                        {"range": {"dates.end": {"lte": search.args["date_to"]}}},
                        {"term": {"dates.all_day": True}},
                    ],
                },
            },
        ]
    elif date_from and date_to:
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
                        {"range": {"dates.start": {"gte": search.args["date_from"]}}},
                        {"range": {"dates.end": {"lte": search.args["date_to"]}}},
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
                        {"range": {"dates.start": {"lt": search.args["date_from"]}}},
                        {"range": {"dates.end": {"gt": search.args["date_to"]}}},
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
                        {"range": {"dates.start": {"gte": search.args["date_from"], "lte": search.args["date_to"]}}},
                        {"range": {"dates.end": {"gte": search.args["date_from"], "lte": search.args["date_to"]}}},
                    ],
                    "filter": {"term": {"dates.all_day": True}},
                    "minimum_should_match": 1,
                },
            },
        ]

    if search.item_type == "events":
        # Get events for extra dates for coverages and planning.
        should.append({"range": {"display_dates": date_range}})

    if len(should):
        search.query["bool"]["filter"].append({"bool": {"should": should, "minimum_should_match": 1}})


aggregations: Dict[str, Dict[str, Any]] = {
    "language": {"terms": {"field": "language"}},
    "calendar": {"terms": {"field": "calendars.name", "size": 100}},
    "service": {"terms": {"field": "service.name", "size": 50}},
    "subject": {"terms": {"field": "subject.name", "size": 20}},
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
            "service": {"terms": {"field": "planning_items.service.name", "size": 50}},
            "subject": {"terms": {"field": "planning_items.subject.name", "size": 20}},
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


def get_agenda_aggregations(events_only=False):
    aggs = deepcopy(aggregations)
    if events_only:
        aggs.pop("coverage", None)
        aggs.pop("planning_items", None)
        aggs.pop("urgency", None)
        aggs.pop("agendas", None)
    return aggs


def get_aggregation_field(key: str):
    if key == "coverage":
        return aggregations[key]["aggs"]["coverage_type"]["terms"]["field"]
    elif key == "agendas":
        return aggregations[key]["aggs"]["agenda"]["terms"]["field"]
    elif is_search_field_nested("agenda", key):
        return aggregations[key]["aggs"][f"{key}_filtered"]["aggs"][key]["terms"]["field"]
    return aggregations[key]["terms"]["field"]


def nested_query(path, query, inner_hits=True, name=None):
    nested = {"path": path, "query": query}
    if inner_hits:
        nested["inner_hits"] = {}
        if name:
            nested["inner_hits"]["name"] = name

    return {"nested": nested}


coverage_filters = ["coverage", "coverage_status"]
planning_filters = coverage_filters + ["agendas"]


def _filter_terms(filters, item_type):
    must_term_filters = []
    must_not_term_filters = []
    for key, val in filters.items():
        if not val:
            continue
        elif item_type == "events" and key in planning_filters:
            continue
        elif key == "location":
            search_type = val.get("type", "location")

            if search_type == "city":
                field = "location.address.city.keyword"
            elif search_type == "state":
                field = "location.address.state.keyword"
            elif search_type == "country":
                field = "location.address.country.keyword"
            else:
                field = "location.name.keyword"

            must_term_filters.append({"term": {field: val.get("name")}})
        elif key == "coverage":
            must_term_filters.append(
                nested_query(
                    path="coverages",
                    query={"bool": {"filter": [{"terms": {get_aggregation_field(key): val}}]}},
                    name="coverage",
                )
            )
        elif key == "coverage_status":
            if val == ["planned"]:
                must_term_filters.append(
                    nested_query(
                        path="coverages",
                        query={"bool": {"filter": [{"terms": {"coverages.coverage_status": ["coverage intended"]}}]}},
                        name="coverage_status",
                    )
                )
            else:
                must_not_term_filters.append(
                    nested_query(
                        path="coverages",
                        query={"bool": {"filter": [{"terms": {"coverages.coverage_status": ["coverage intended"]}}]}},
                        name="coverage_status",
                    )
                )
        elif key == "agendas":
            must_term_filters.append(
                nested_query(
                    path="planning_items",
                    query={"bool": {"filter": [{"terms": {get_aggregation_field(key): val}}]}},
                    name="agendas",
                )
            )
        else:
            if item_type != "events":
                agg_field = get_aggregation_field(key)
                must_term_filters.append(
                    {
                        "bool": {
                            "minimum_should_match": 1,
                            "should": [
                                get_filter_query(key, val, agg_field, get_nested_config("agenda", key)),
                                nested_query(
                                    path="planning_items",
                                    query={"bool": {"filter": [{"terms": {f"planning_items.{agg_field}": val}}]}},
                                    name=key,
                                ),
                            ],
                        },
                    }
                )
            else:
                must_term_filters.append(
                    get_filter_query(key, val, get_aggregation_field(key), get_nested_config("agenda", key))
                )

    return {
        "must_term_filters": must_term_filters,
        "must_not_term_filters": must_not_term_filters,
    }


def _remove_fields(source, fields):
    """Add fields to remove the elastic search

    :param dict source: elasticsearch query object
    :param fields: list of fields
    """
    if not source.get("_source"):
        source["_source"] = {}

    if not source.get("_source").get("exclude"):
        source["_source"]["exclude"] = []

    source["_source"]["exclude"].extend(fields)


def planning_items_query_string(query, fields=None):
    plan_query_string = query_string(query)

    if fields:
        plan_query_string["query_string"]["fields"] = fields
    else:
        plan_query_string["query_string"]["fields"] = ["planning_items.*"]

    return plan_query_string


def get_agenda_query(query, events_only=False):
    if events_only:
        return query_string(query)
    else:
        return {
            "bool": {
                "should": [
                    query_string(query),
                    nested_query("planning_items", planning_items_query_string(query), name="query"),
                ]
            },
        }


def is_events_only_access(user, company):
    if user and company and not is_admin(user):
        return company.get("events_only", False)
    return False


def filter_active_users(user_ids, user_dict, company_dict, events_only=False):
    active = []
    for _id in user_ids:
        user = user_dict.get(str(_id))
        if user and (not user.get("company") or str(user.get("company", "")) in company_dict):
            if (
                events_only
                and user.get("company")
                and (company_dict.get(str(user.get("company", ""))) or {}).get("events_only")
            ):
                continue
            active.append(_id)
    return active


class AgendaService(BaseSearchService):
    section = "agenda"
    limit_days_setting = None
    default_sort = [{"dates.start": "asc"}]
    default_page_size = 100

    def on_fetched(self, doc):
        self.enhance_items(doc[config.ITEMS])

    def on_fetched_item(self, doc):
        self.enhance_items([doc])

    def enhance_items(self, docs):
        for doc in docs:
            self.enhance_coverages(doc.get("coverages") or [])
            doc.setdefault("_hits", {})
            doc["_hits"]["matched_event"] = doc.pop("_search_matched_event", False)

            if not doc.get("planning_items"):
                continue

            doc["_hits"]["matched_planning_items"] = [plan["_id"] for plan in doc.get("planning_items") or []]

            # Filter based on _inner_hits
            inner_hits = doc.pop("_inner_hits", {})

            # If the search matched the Event
            # then only count Planning based filters when checking ``_inner_hits``
            if doc["_hits"]["matched_event"]:
                inner_hits = {key: val for key, val in inner_hits.items() if key in planning_filters}

            if not inner_hits or not doc.get("planning_items"):
                continue

            if len([f for f in inner_hits.keys() if f in coverage_filters]) > 0:
                # Collect hits for 'coverage' and 'coverage_status' separately to other inner_hits
                coverages_by_filter = {
                    key: [item.get("coverage_id") for item in items]
                    for key, items in inner_hits.items()
                    if key in ["coverage", "coverage_status"]
                }
                unique_coverage_ids = set(
                    [coverage_id for items in coverages_by_filter.values() for coverage_id in items]
                )
                doc["_hits"]["matched_coverages"] = [
                    coverage_id
                    for coverage_id in unique_coverage_ids
                    if all([coverage_id in items for items in coverages_by_filter.values()])
                ]

            if doc["item_type"] == "planning":
                # If this is a Planning item, then ``inner_hits`` should only include the
                # fields relevant to the Coverages (as this is the only nested field of a Planning item)
                inner_hits = {key: val for key, val in inner_hits.items() if key in planning_filters}

            if len(inner_hits.keys()) > 0:
                # Store matched Planning IDs into matched_planning_items
                # The Planning IDs must be in all supplied ``_inner_hits``
                # In order to be included (i.e. match all nested planning queries)
                items_by_filter = {
                    key: [item.get("guid") or item.get("planning_id") for item in items]
                    for key, items in inner_hits.items()
                }
                unique_ids = set([item_id for items in items_by_filter.values() for item_id in items])
                doc["_hits"]["matched_planning_items"] = [
                    item_id for item_id in unique_ids if all([item_id in items for items in items_by_filter.values()])
                ]

    def enhance_coverages(self, coverages):
        completed_coverages = [
            c
            for c in coverages
            if c["workflow_status"] == ASSIGNMENT_WORKFLOW_STATE.COMPLETED and len(c.get("deliveries") or []) > 0
        ]
        # Enhance completed coverages in general - add story's abstract/headline/slugline
        text_delivery_ids = [
            c.get("delivery_id")
            for c in completed_coverages
            if c.get("delivery_id") and c.get("coverage_type") == "text"
        ]
        wire_search_service = get_resource_service("wire_search")
        if text_delivery_ids:
            wire_items = wire_search_service.get_items(text_delivery_ids)
            if wire_items.count() > 0:
                for item in wire_items:
                    c = [c for c in completed_coverages if c.get("delivery_id") == item.get("_id")][0]
                    self.enhance_coverage_with_wire_details(c, item)

        media_coverages = [c for c in completed_coverages if c.get("coverage_type") != "text"]
        for c in media_coverages:
            try:
                c["deliveries"][0]["delivery_href"] = c["delivery_href"] = app.set_photo_coverage_href(
                    c, None, c["deliveries"]
                )
            except Exception as e:
                logger.exception(e)
                logger.error("Failed to generate delivery_href for coverage={}".format(c.get("coverage_id")))

    def enhance_coverage_with_wire_details(self, coverage, wire_item):
        coverage["publish_time"] = wire_item.get("publish_schedule") or wire_item.get("firstpublished")

    def get(self, req, lookup):
        if req.args.get("featured"):
            return self.get_featured_stories(req, lookup)

        cursor = super().get(req, lookup)

        args = req.args
        if args.get("itemType") is None or (args.get("date_from") and args.get("date_to")):
            matching_event_ids: Set[str] = (
                set() if args.get("itemType") is not None else self._get_event_ids_matching_query(req, lookup)
            )
            date_range = {} if not (args.get("date_from") and args.get("date_to")) else get_date_filters(args)

            for doc in cursor.docs:
                if doc["_id"] in matching_event_ids:
                    doc["_search_matched_event"] = True
                if date_range:
                    # make the items display on the featured day,
                    # it's used in ui instead of dates.start and dates.end
                    doc.update(
                        {
                            "_display_from": date_range.get("gt"),
                            "_display_to": date_range.get("lt"),
                        }
                    )

        return cursor

    def _get_event_ids_matching_query(self, req, lookup) -> Set[str]:
        """Re-run the query to retrieve the list of Event IDs matching the query

        This is used to show ALL Planning Items for the Event if the search query matched the parent Event
        """

        orig_args = req.args
        req.args = {key: val for key, val in dict(req.args).items() if key not in planning_filters}
        req.args["itemType"] = "events"
        req.args["noAggregations"] = 1
        req.projection = json.dumps({"_id": 1})
        item_ids = set([item["_id"] for item in super().get(req, lookup)])
        req.args = orig_args
        return item_ids

    def prefill_search_query(self, search: SearchQuery, req=None, lookup=None):
        """Generate the search query instance

        :param newsroom.search.SearchQuery search: The search query instance
        :param ParsedRequest req: The parsed in request instance from the endpoint
        :param dict lookup: The parsed in lookup dictionary from the endpoint
        """

        super().prefill_search_query(search, req, lookup)
        search.item_type = (
            "events" if is_events_only_access(search.user, search.company) else search.args.get("itemType")
        )

    def prefill_search_items(self, search):
        """Prefill the item filters

        :param newsroom.search.SearchQuery search: The search query instance
        """

        pass

    def apply_filters(self, search):
        """Generate and apply the different search filters

        :param newsroom.search.SearchQuery search: the search query instance
        """

        # First construct the product query
        self.apply_company_filter(search)

        search.planning_items_should = []
        self.apply_products_filter(search)

        if search.planning_items_should:
            search.query["bool"]["should"].append(
                nested_query(
                    "planning_items",
                    {
                        "bool": {
                            "should": search.planning_items_should,
                            "minimum_should_match": 1,
                        }
                    },
                    name="products",
                )
            )
            search.query["bool"]["minimum_should_match"] = 1

        # Append the product query to the agenda query
        agenda_query = _agenda_query()
        agenda_query["bool"]["filter"].append(search.query)
        search.query = agenda_query

        # Apply agenda based filters
        self.apply_section_filter(search)
        self.apply_request_filter(search)

        if not is_admin_or_internal(search.user):
            _remove_fields(search.source, PRIVATE_FIELDS)

        if search.item_type == "events":
            # no adhoc planning items and remove planning items and coverages fields
            search.query["bool"]["filter"].append(
                {
                    "bool": {
                        "should": [
                            {"term": {"item_type": "event"}},
                            {
                                # Match Events before ``item_type`` field was added
                                "bool": {
                                    "must_not": {"exists": {"field": "item_type"}},
                                    "filter": {"exists": {"field": "event_id"}},
                                },
                            },
                        ],
                        "minimum_should_match": 1,
                    },
                }
            )
            _remove_fields(search.source, PLANNING_ITEMS_FIELDS)
        elif search.item_type == "planning":
            search.query["bool"]["filter"].append(
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
        else:
            # Don't include Planning items that are associated with an Event
            search.query["bool"]["filter"].append(
                {
                    "bool": {
                        "should": [
                            {"bool": {"must_not": {"exists": {"field": "item_type"}}}},
                            {"term": {"item_type": "event"}},
                            {
                                "bool": {
                                    "filter": {"term": {"item_type": "planning"}},
                                    "must_not": {"exists": {"field": "event_id"}},
                                },
                            },
                        ],
                        "minimum_should_match": 1,
                    },
                }
            )

    def apply_product_filter(self, search, product):
        """Generate the filter for a single product

        :param newsroom.search.SearchQuery search: The search query instance
        :param dict product: The product to filter
        :return:
        """
        if search.args.get("requested_products") and product["_id"] not in search.args["requested_products"]:
            return

        if product.get("query"):
            search.query["bool"]["should"].append(query_string(product["query"]))

            if product.get("planning_item_query") and search.item_type != "events":
                search.planning_items_should.append(planning_items_query_string(product.get("planning_item_query")))

    def apply_request_filter(self, search):
        """Generate the request filters

        :param newsroom.search.SearchQuery search: The search query instance
        """

        if search.args.get("q"):
            test_query = {"bool": {"should": []}}
            try:
                q = json.loads(search.args.get("q"))
                if isinstance(q, dict):
                    # used for product testing
                    if q.get("query"):
                        test_query["bool"]["should"].append(query_string(q.get("query")))

                    if q.get("planning_item_query"):
                        test_query["bool"]["should"].append(
                            nested_query(
                                "planning_items",
                                planning_items_query_string(q.get("planning_item_query")),
                                name="product_test",
                            )
                        )

                    if test_query["bool"]["should"]:
                        search.query["bool"]["filter"].append(test_query)
            except Exception:
                pass

            if not test_query["bool"]["should"]:
                search.query["bool"]["filter"].append(get_agenda_query(search.args["q"], search.item_type == "events"))

        if search.args.get("id"):
            search.query["bool"]["filter"].append({"term": {"_id": search.args["id"]}})

        if search.args.get("bookmarks"):
            set_saved_items_query(search.query, search.args["bookmarks"])

        if search.args.get("date_from") or search.args.get("date_to"):
            _set_event_date_range(search)

    def set_post_filter(self, source: Dict[str, Any], req: ParsedRequest, item_type: Optional[str] = None):
        filters = json.loads(req.args.get("filter") or "{}")
        if not filters:
            return

        if app.config.get("FILTER_BY_POST_FILTER", False):
            source["post_filter"] = {"bool": {}}
            self.set_bool_query_from_filters(source["post_filter"]["bool"], filters, item_type)
        else:
            self.set_bool_query_from_filters(source["query"]["bool"], filters, item_type)

    def gen_source_from_search(self, search):
        """Generate the eve source object from the search query instance

        :param newsroom.search.SearchQuery search: The search query instance
        """

        super().gen_source_from_search(search)

        self.set_post_filter(search.source, search, search.item_type)

        if not search.source["from"] and not search.args.get("bookmarks") and not search.args.get("noAggregations"):
            # avoid aggregations when handling pagination
            search.source["aggs"] = get_agenda_aggregations(search.item_type == "events")
        else:
            search.source.pop("aggs", None)

    def featured(self, req, lookup, featured):
        """Return featured items.

        :param ParsedRequest req: The parsed in request instance from the endpoint
        :param dict lookup: The parsed in lookup dictionary from the endpoint
        :param dict featured: list featured items
        """
        user = get_user()
        company = get_company(user)
        if is_events_only_access(user, company):
            abort(403)

        if not featured or not featured.get("items"):
            return ListCursor([])

        query = _agenda_query()
        get_resource_service("section_filters").apply_section_filter(query, self.section)
        planning_items_query = nested_query(
            "planning_items",
            {"bool": {"filter": [{"terms": {"planning_items.guid": featured["items"]}}]}},
            name="featured",
        )
        if req.args.get("q"):
            query["bool"]["filter"].append(query_string(req.args["q"]))
            planning_items_query["nested"]["query"]["bool"]["filter"].append(planning_items_query_string(req.args["q"]))

        query["bool"]["filter"].append(planning_items_query)

        source = {"query": query}
        self.set_post_filter(source, req)
        source["size"] = len(featured["items"])
        source["from"] = req.args.get("from", 0, type=int)
        if not source["from"]:
            source["aggs"] = aggregations

        if company and not is_admin(user) and company.get("events_only", False):
            # no adhoc planning items and remove planning items and coverages fields
            query["bool"]["filter"].append({"exists": {"field": "event"}})
            _remove_fields(source, PLANNING_ITEMS_FIELDS)

        internal_req = ParsedRequest()
        internal_req.args = {"source": json.dumps(source)}
        cursor = self.internal_get(internal_req, lookup)

        docs_by_id = {}
        for doc in cursor.docs:
            for p in doc.get("planning_items") or []:
                docs_by_id[p.get("guid")] = doc

            # make the items display on the featured day,
            # it's used in ui instead of dates.start and dates.end
            doc.update(
                {
                    "_display_from": featured["display_from"],
                    "_display_to": featured["display_to"],
                }
            )

        docs = []
        agenda_ids = set()
        for _id in featured["items"]:
            if docs_by_id.get(_id) and docs_by_id.get(_id).get("_id") not in agenda_ids:
                docs.append(docs_by_id.get(_id))
                agenda_ids.add(docs_by_id.get(_id).get("_id"))

        cursor.docs = docs
        return cursor

    def get_items(self, item_ids):
        query = {
            "bool": {
                "filter": [{"terms": {"_id": item_ids}}],
            }
        }
        get_resource_service("section_filters").apply_section_filter(query, self.section)
        return self.get_items_by_query(query, size=len(item_ids))

    def get_items_by_query(self, query, size=50):
        try:
            source = {"query": query}

            if size:
                source["size"] = size

            req = ParsedRequest()
            req.args = {"source": json.dumps(source)}

            return self.internal_get(req, None)
        except Exception as exc:
            logger.error(
                "Error in get_items for agenda query: {}".format(json.dumps(source)),
                exc,
                exc_info=True,
            )

    def get_matching_bookmarks(self, item_ids, active_users, active_companies):
        """Returns a list of user ids bookmarked any of the given items

        :param item_ids: list of ids of items to be searched
        :param active_users: user_id, user dictionary
        :param active_companies: company_id, company dictionary
        :return:
        """
        bookmark_users = []

        search_results = self.get_items(item_ids)

        if not search_results:
            return bookmark_users

        for result in search_results.hits["hits"]["hits"]:
            bookmarks = result["_source"].get("watches", [])
            for bookmark in bookmarks:
                user = active_users.get(bookmark)
                if user and str(user.get("company", "")) in active_companies:
                    bookmark_users.append(bookmark)

        return bookmark_users

    def set_delivery(self, wire_item):
        if not wire_item.get("coverage_id"):
            return

        def is_delivery_validated(coverage, item):
            latest_delivery = get_latest_available_delivery(coverage)
            if not latest_delivery or not item.get("rewrite_sequence"):
                return True

            if (item.get("rewrite_sequence") or 0) >= latest_delivery.get("sequence_no", 0) or (
                item.get("publish_schedule") or item.get("firstpublished")
            ) >= latest_delivery.get("publish_time"):
                return True

            return False

        query = {
            "bool": {
                "filter": [
                    {
                        "nested": {
                            "path": "coverages",
                            "query": {
                                "bool": {"filter": [{"term": {"coverages.coverage_id": wire_item["coverage_id"]}}]}
                            },
                        }
                    }
                ],
            }
        }

        agenda_items = self.get_items_by_query(query)
        agenda_updated_notification_sent = False

        def update_coverage_details(coverage):
            coverage["delivery_id"] = wire_item["guid"]
            coverage["delivery_href"] = url_for_wire(
                None,
                _external=False,
                section="wire.item",
                _id=wire_item["guid"],
            )
            coverage["workflow_status"] = ASSIGNMENT_WORKFLOW_STATE.COMPLETED
            deliveries = coverage.get("deliveries") or []
            d = next(
                (d for d in deliveries if d.get("delivery_id") == wire_item["guid"]),
                None,
            )
            if d and d.get("delivery_state") != "published":
                d["delivery_state"] = "published"
                d["publish_time"] = parse_date_str(wire_item.get("publish_schedule") or wire_item.get("firstpublished"))
            return d

        for item in agenda_items:
            self.enhance_coverage_watches(item)

            parent_coverage = next(
                (c for c in item.get("coverages") or [] if c["coverage_id"] == wire_item["coverage_id"]), None
            )
            if not parent_coverage or not is_delivery_validated(parent_coverage, item):
                continue

            delivery = update_coverage_details(parent_coverage)
            planning_item = next(
                (p for p in item.get("planning_items") or [] if p["_id"] == parent_coverage["planning_id"]), None
            )
            planning_updated = False
            if planning_item:
                coverage = next(
                    (c for c in planning_item.get("coverages") or [] if c["coverage_id"] == wire_item["coverage_id"]),
                    None,
                )
                if coverage:
                    planning_updated = True
                    update_coverage_details(coverage)

            if not planning_updated:
                self.system_update(item["_id"], {"coverages": item["coverages"]}, item)
            else:
                updates = {
                    "coverages": item["coverages"],
                    "planning_items": item["planning_items"],
                }
                self.system_update(item["_id"], updates, item)

            updated_agenda = get_entity_or_404(item.get("_id"), "agenda")
            # Notify agenda to update itself with new details of coverage
            self.enhance_coverage_with_wire_details(parent_coverage, wire_item)
            push_agenda_item_notification("new_item", item=item)

            # If published first time, coverage completion will trigger email - not needed now
            if (delivery or {}).get("sequence_no", 0) > 0 and not agenda_updated_notification_sent:
                agenda_updated_notification_sent = True
                self.notify_agenda_update(updated_agenda, updated_agenda, None, True, None, parent_coverage)
        return agenda_items

    def set_bool_query_from_filters(
        self, bool_query: Dict[str, Any], filters: Dict[str, Any], item_type: Optional[str] = None
    ):
        filter_terms = _filter_terms(filters, item_type)
        bool_query.setdefault("filter", [])
        bool_query["filter"] += filter_terms["must_term_filters"]

        bool_query.setdefault("must_not", [])
        bool_query["must_not"] += filter_terms["must_not_term_filters"]

    def get_matching_topics(self, item_id, topics, users, companies):
        """Returns a list of topic ids matching to the given item_id

        :param item_id: item id to be tested against all topics
        :param topics: list of topics
        :param users: user_id, user dictionary
        :param companies: company_id, company dictionary
        :return:
        """

        return self.get_matching_topics_for_item(
            topics,
            users,
            companies,
            {
                "bool": {
                    "must_not": [
                        {"term": {"state": "killed"}},
                    ],
                    "filter": [
                        {"term": {"_id": item_id}},
                    ],
                    "should": [],
                }
            },
        )

    def enhance_coverage_watches(self, item):
        for c in item.get("coverages") or []:
            if c.get("watches"):
                c["watches"] = [ObjectId(u) for u in c["watches"]]

    def notify_new_coverage(self, agenda, wire_item):
        user_dict = get_user_dict()
        company_dict = get_company_dict()
        notify_user_ids = filter_active_users(agenda.get("watches", []), user_dict, company_dict, events_only=True)
        for user_id in notify_user_ids:
            user = user_dict[str(user_id)]
            send_coverage_notification_email(user, agenda, wire_item)

    def notify_agenda_update(
        self,
        update_agenda,
        original_agenda,
        item=None,
        events_only=False,
        related_planning_removed=None,
        coverage_updated=None,
    ):
        agenda = deepcopy(update_agenda)
        if agenda and original_agenda.get("state") != WORKFLOW_STATE.KILLED:
            user_dict = get_user_dict()
            company_dict = get_company_dict()
            coverage_watched = None
            for c in original_agenda.get("coverages") or []:
                if len(c.get("watches") or []) > 0:
                    coverage_watched = True
                    break

            notify_user_ids = filter_active_users(
                original_agenda.get("watches", []), user_dict, company_dict, events_only
            )

            users = [user_dict[str(user_id)] for user_id in notify_user_ids]

            if len(notify_user_ids) == 0 and not coverage_watched:
                return

            def get_detailed_coverage(cov):
                plan = next(
                    (p for p in (agenda.get("planning_items") or []) if p["guid"] == cov.get("planning_id")),
                    None,
                )
                if plan and plan.get("state") != WORKFLOW_STATE.KILLED:
                    detail_cov = next(
                        (c for c in (plan.get("coverages") or []) if c.get("coverage_id") == cov.get("coverage_id")),
                        None,
                    )
                    if detail_cov:
                        detail_cov["watches"] = cov.get("watches")

                    return detail_cov

                original_cov = next(
                    (c for c in original_agenda.get("coverages") or [] if c["coverage_id"] == cov["coverage_id"]),
                    cov,
                )
                cov["watches"] = original_cov.get("watches") or []
                return cov

            def fill_all_coverages(skip_coverages=[], cancelled=False, use_original_agenda=False):
                fill_list = (
                    coverage_updates["unaltered_coverages"]
                    if not cancelled
                    else coverage_updates["cancelled_coverages"]
                )
                for coverage in (agenda if not use_original_agenda else original_agenda).get("coverages") or []:
                    if not next(
                        (s for s in skip_coverages if s.get("coverage_id") == coverage.get("coverage_id")),
                        None,
                    ):
                        detailed_coverage = get_detailed_coverage(coverage)
                        if detailed_coverage:
                            fill_list.append(detailed_coverage)

            coverage_updates = {
                "modified_coverages": [] if not coverage_updated else [coverage_updated],
                "cancelled_coverages": [],
                "unaltered_coverages": [],
            }

            only_new_coverages = len(coverage_updates["modified_coverages"]) == 0
            time_updated = False
            state_changed = False
            coverage_modified = False

            # Send notification for only these state changes
            notify_states = [
                WORKFLOW_STATE.CANCELLED,
                WORKFLOW_STATE.RESCHEDULED,
                WORKFLOW_STATE.POSTPONED,
                WORKFLOW_STATE.KILLED,
                WORKFLOW_STATE.SCHEDULED,
            ]

            if not coverage_updated:  # If not story updates - but from planning side
                if not related_planning_removed:
                    # Send notification if time got updated
                    if original_agenda.get("dates") and agenda.get("dates"):
                        time_updated = (original_agenda.get("dates") or {}).get("start").replace(tzinfo=None) != (
                            agenda.get("dates") or {}
                        ).get("start").replace(tzinfo=None) or (original_agenda.get("dates") or {}).get("end").replace(
                            tzinfo=None
                        ) != (
                            agenda.get("dates") or {}
                        ).get(
                            "end"
                        ).replace(
                            tzinfo=None
                        )

                    if agenda.get("state") and agenda.get("state") != original_agenda.get("state"):
                        state_changed = agenda.get("state") in notify_states

                    if not state_changed:
                        if time_updated:
                            fill_all_coverages()
                        else:
                            for coverage in agenda.get("coverages") or []:
                                existing_coverage = next(
                                    (
                                        c
                                        for c in original_agenda.get("coverages") or []
                                        if c["coverage_id"] == coverage["coverage_id"]
                                    ),
                                    None,
                                )
                                detailed_coverage = get_detailed_coverage(coverage)
                                if detailed_coverage:
                                    if not existing_coverage:
                                        if coverage["workflow_status"] != WORKFLOW_STATE.CANCELLED:
                                            coverage_updates["modified_coverages"].append(detailed_coverage)
                                    elif coverage.get(
                                        "workflow_status"
                                    ) == WORKFLOW_STATE.CANCELLED and existing_coverage.get(
                                        "workflow_status"
                                    ) != coverage.get(
                                        "workflow_status"
                                    ):
                                        coverage_updates["cancelled_coverages"].append(detailed_coverage)
                                    elif (
                                        (
                                            coverage.get("delivery_state") != existing_coverage.get("delivery_state")
                                            and coverage.get("delivery_state") == "published"
                                        )
                                        or (
                                            coverage.get("workflow_status") != existing_coverage.get("workflow_status")
                                            and coverage.get("workflow_status") == "completed"
                                        )
                                        or (existing_coverage.get("scheduled") != coverage.get("scheduled"))
                                    ):
                                        coverage_updates["modified_coverages"].append(detailed_coverage)
                                        only_new_coverages = False
                                    elif detailed_coverage["coverage_id"] != (coverage_updated or {}).get(
                                        "coverage_id"
                                    ):
                                        coverage_updates["unaltered_coverages"].append(detailed_coverage)

                            # Check for removed coverages - show it as cancelled
                            if item and item.get("type") == "planning":
                                for original_cov in original_agenda.get("coverages") or []:
                                    updated_cov = next(
                                        (
                                            c
                                            for c in (agenda.get("coverages") or [])
                                            if c.get("coverage_id") == original_cov.get("coverage_id")
                                        ),
                                        None,
                                    )
                                    if not updated_cov:
                                        coverage_updates["cancelled_coverages"].append(original_cov)
                    else:
                        fill_all_coverages(
                            cancelled=False if agenda.get("state") == WORKFLOW_STATE.SCHEDULED else True,
                            use_original_agenda=True,
                        )
                else:
                    fill_all_coverages(related_planning_removed.get("coverages") or [])
                    # Add removed coverages:
                    for coverage in related_planning_removed.get("coverages") or []:
                        detailed_coverage = get_detailed_coverage(coverage)
                        if detailed_coverage:
                            coverage_updates["cancelled_coverages"].append(detailed_coverage)

            if len(coverage_updates["modified_coverages"]) > 0 or len(coverage_updates["cancelled_coverages"]) > 0:
                coverage_modified = True

            if coverage_updated or related_planning_removed or time_updated or state_changed or coverage_modified:
                agenda["name"] = agenda.get("name", original_agenda.get("name"))
                agenda["definition_short"] = agenda.get("definition_short", original_agenda.get("definition_short"))
                agenda["ednote"] = agenda.get("ednote", original_agenda.get("ednote"))
                agenda["state_reason"] = agenda.get("state_reason", original_agenda.get("state_reason"))
                action = "been updated."
                if state_changed:
                    action = "been {}.".format(
                        agenda.get("state")
                        if agenda.get("state") != WORKFLOW_STATE.KILLED
                        else "removed from the calendar"
                    )

                if (
                    len(coverage_updates["modified_coverages"]) > 0
                    and only_new_coverages
                    and len(coverage_updates["cancelled_coverages"]) == 0
                ):
                    action = "new coverage(s)."

                message = "The {} you have been following has {}".format(
                    "event" if agenda.get("event") else "coverage plan", action
                )
                if agenda.get("state_reason"):
                    reason_prefix = agenda.get("state_reason").find(":")
                    if reason_prefix > 0:
                        message = "{} {}".format(
                            message,
                            agenda["state_reason"][(reason_prefix + 1) : len(agenda["state_reason"])],
                        )

                # append coverage watching users too - except for unaltered_coverages
                for c in coverage_updates["cancelled_coverages"] + coverage_updates["modified_coverages"]:
                    if c.get("watches"):
                        notify_user_ids = filter_active_users(c["watches"], user_dict, company_dict, events_only)
                        users = users + [user_dict[str(user_id)] for user_id in notify_user_ids]

                # Send notifications to users
                save_user_notifications(
                    [
                        UserNotification(
                            user=user["_id"],
                            item=agenda.get("_id"),
                            resource="agenda",
                            action="watched_agenda_updated",
                            data=None,
                        )
                        for user in users
                    ]
                )

                for user in users:
                    send_agenda_notification_email(
                        user,
                        agenda,
                        message,
                        original_agenda,
                        coverage_updates,
                        related_planning_removed,
                        coverage_updated,
                        time_updated,
                        coverage_modified,
                    )

    def get_saved_items_count(self):
        search = SearchQuery()
        search.query = _agenda_query()

        self.prefill_search_query(search)
        self.apply_filters(search)
        set_saved_items_query(search.query, str(search.user["_id"]))

        cursor = self.get_items_by_query(search.query, size=0)
        return cursor.count() if cursor else 0

    def get_featured_stories(self, req, lookup):
        for_date = datetime.strptime(req.args.get("date_from"), "%d/%m/%Y %H:%M")
        offset = int(req.args.get("timezone_offset", "0"))
        local_date = get_local_date(
            for_date.strftime("%Y-%m-%d"),
            datetime.strftime(for_date, "%H:%M:%S"),
            offset,
        )
        featured_doc = get_resource_service("agenda_featured").find_one_for_date(local_date)
        return self.featured(req, lookup, featured_doc)
