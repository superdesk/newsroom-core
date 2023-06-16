import json

import flask
from flask import current_app as app, request
from flask_babel import gettext
from eve.methods.get import get_internal
from eve.render import send_response
from eve.utils import ParsedRequest
from superdesk import get_resource_service

from newsroom.agenda import blueprint
from newsroom.template_filters import is_admin_or_internal, is_admin
from newsroom.topics import get_company_folders, get_user_folders, get_user_topics
from newsroom.navigations.navigations import get_navigations_by_company
from newsroom.auth import get_company, get_user, get_user_id
from newsroom.decorator import login_required, section
from newsroom.utils import (
    get_entity_or_404,
    is_json_request,
    get_json_or_400,
    get_entities_elastic_or_mongo_or_404,
    get_agenda_dates,
    get_location_string,
    get_public_contacts,
    get_links,
    get_vocabulary,
)
from newsroom.wire.utils import update_action_list
from newsroom.wire.views import set_item_permission
from newsroom.agenda.email import send_coverage_request_email
from newsroom.agenda.utils import remove_fields_for_public_user, remove_restricted_coverage_info
from newsroom.companies.utils import restrict_coverage_info
from newsroom.notifications import push_user_notification
from newsroom.search.config import merge_planning_aggs


@blueprint.route("/agenda")
@login_required
@section("agenda")
def index():
    return flask.render_template("agenda_index.html", data=get_view_data())


@blueprint.route("/bookmarks_agenda")
@login_required
def bookmarks():
    data = get_view_data()
    data["bookmarks"] = True
    return flask.render_template("agenda_bookmarks.html", data=data)


@blueprint.route("/agenda/<_id>")
@login_required
def item(_id):
    item = get_entity_or_404(_id, "agenda")

    user = get_user()
    company = get_company(user)
    if not is_admin_or_internal(user):
        remove_fields_for_public_user(item)

    if company and not is_admin(user) and company.get("events_only", False):
        # if the company has permission events only permission then
        # remove planning items and coverages.
        if not item.get("event"):
            # for adhoc planning items abort the request
            flask.abort(403)

        item.pop("planning_items", None)
        item.pop("coverages", None)

    if restrict_coverage_info(company):
        remove_restricted_coverage_info([item])

    if is_json_request(flask.request):
        return flask.jsonify(item)

    if "print" in flask.request.args:
        map = flask.request.args.get("map")
        template = "agenda_item_print.html"
        update_action_list([_id], "prints", force_insert=True)
        get_resource_service("history").create_history_record(
            [item], "print", get_user(), request.args.get("type", "agenda")
        )
        return flask.render_template(
            template,
            item=item,
            map=map,
            dateString=get_agenda_dates(item),
            location=get_location_string(item),
            contacts=get_public_contacts(item),
            links=get_links(item),
            is_admin=is_admin_or_internal(user),
        )

    data = get_view_data()
    data["item"] = item
    return flask.render_template("agenda_index.html", data=data, title=item.get("name", item.get("headline")))


@blueprint.route("/agenda/search")
@login_required
@section("agenda")
def search():
    response = get_internal("agenda")
    if len(response):
        if restrict_coverage_info(get_company()):
            remove_restricted_coverage_info(response[0].get("_items") or [])
        if response[0].get("_aggregations"):
            merge_planning_aggs(response[0]["_aggregations"])
    return send_response("agenda", response)


def get_view_data():
    user = get_user()
    topics = get_user_topics(user["_id"]) if user else []
    company = get_company(user) or {}
    return {
        "user": user,
        "company": str(user["company"]) if user and user.get("company") else None,
        "topics": [t for t in topics if t.get("topic_type") == "agenda"],
        "formats": [
            {"format": f["format"], "name": f["name"]}
            for f in app.download_formatters.values()
            if "agenda" in f["types"]
        ],
        "navigations": get_navigations_by_company(
            company,
            product_type="agenda",
            events_only=company.get("events_only", False),
        )
        if company
        else [],
        "saved_items": get_resource_service("agenda").get_saved_items_count(),
        "events_only": company.get("events_only", False),
        "restrict_coverage_info": company.get("restrict_coverage_info", False),
        "locators": get_vocabulary("locators"),
        "ui_config": get_resource_service("ui_config").get_section_config("agenda"),
        "groups": app.config.get("AGENDA_GROUPS", []),
        "has_agenda_featured_items": get_resource_service("agenda_featured").find_one(req=None) is not None,
        "user_folders": get_user_folders(user, "agenda") if user else [],
        "company_folders": get_company_folders(company, "agenda") if company else [],
    }


@blueprint.route("/agenda/request_coverage", methods=["POST"])
@login_required
def request_coverage():
    user = get_user(required=True)
    data = get_json_or_400()
    assert data.get("item")
    assert data.get("message")
    item = get_entity_or_404(data.get("item"), "agenda")
    send_coverage_request_email(user, data.get("message"), item)
    return flask.jsonify(), 201


@blueprint.route("/agenda_bookmark", methods=["POST", "DELETE"])
@login_required
def bookmark():
    data = get_json_or_400()
    assert data.get("items")
    update_action_list(data.get("items"), "bookmarks", item_type="agenda")
    push_user_notification("saved_items", count=get_resource_service("agenda").get_saved_items_count())
    return flask.jsonify(), 200


@blueprint.route("/agenda_watch", methods=["POST", "DELETE"])
@login_required
def follow():
    data = get_json_or_400()
    assert data.get("items")
    for item_id in data.get("items"):
        user_id = get_user_id()
        item = get_entity_or_404(item_id, "agenda")
        coverage_updates = {"coverages": item.get("coverages") or []}
        for c in coverage_updates["coverages"]:
            if c.get("watches") and user_id in c["watches"]:
                c["watches"].remove(user_id)

        if request.method == "POST":
            updates = {"watches": list(set((item.get("watches") or []) + [user_id]))}
            if item.get("coverages"):
                updates.update(coverage_updates)

            get_resource_service("agenda").patch(item_id, updates)
        else:
            if request.args.get("bookmarks"):
                user_item_watches = [u for u in (item.get("watches") or []) if str(u) == str(user_id)]
                if not user_item_watches:
                    # delete user watches of all coverages
                    get_resource_service("agenda").patch(item_id, coverage_updates)
                    return flask.jsonify(), 200

            update_action_list(data.get("items"), "watches", item_type="agenda")

    push_user_notification("saved_items", count=get_resource_service("agenda").get_saved_items_count())
    return flask.jsonify(), 200


@blueprint.route("/agenda_coverage_watch", methods=["POST", "DELETE"])
@login_required
def watch_coverage():
    user_id = get_user_id()
    data = get_json_or_400()
    assert data.get("item_id")
    assert data.get("coverage_id")
    return update_coverage_watch(data["item_id"], data["coverage_id"], user_id, add=request.method == "POST")


def update_coverage_watch(item_id, coverage_id, user_id, add, skip_associated=False):
    item = get_entity_or_404(item_id, "agenda")

    if user_id in item.get("watches", []):
        return (
            flask.jsonify({"error": gettext("Cannot edit coverage watch when watching parent item")}),
            403,
        )

    try:
        coverage_index = [c["coverage_id"] for c in (item.get("coverages") or [])].index(coverage_id)
    except ValueError:
        return flask.jsonify({"error": gettext("Coverage not found")}), 404

    updates = {"coverages": item["coverages"]}

    if add:
        updates["coverages"][coverage_index]["watches"] = list(
            set((updates["coverages"][coverage_index].get("watches") or []) + [user_id])
        )
    else:
        try:
            updates["coverages"][coverage_index]["watches"].remove(user_id)
        except Exception:
            return flask.jsonify({"error": gettext("Error removing watch.")}), 404

    get_resource_service("agenda").patch(item_id, updates)

    if skip_associated:
        return flask.jsonify(), 200
    elif item.get("item_type") == "planning" and item.get("event_id"):
        # Need to also update the parent Event's list of coverage watches
        return update_coverage_watch(item["event_id"], coverage_id, user_id, add, skip_associated=True)
    elif item.get("item_type") == "event":
        # Need to also update the Planning item's list of coverage watches
        return update_coverage_watch(
            item["coverages"][coverage_index]["planning_id"],
            coverage_id,
            user_id,
            add,
            skip_associated=True,
        )

    return flask.jsonify(), 200


@blueprint.route("/agenda/wire_items/<wire_id>")
@login_required
def related_wire_items(wire_id):
    elastic = app.data._search_backend("agenda")
    source = {}
    must_terms = [{"term": {"coverages.delivery_id": {"value": wire_id}}}]
    query = {
        "bool": {"filter": must_terms},
    }

    source.update({"query": {"nested": {"path": "coverages", "query": query}}})
    internal_req = ParsedRequest()
    internal_req.args = {"source": json.dumps(source)}
    agenda_result, _ = elastic.find("agenda", internal_req, None)

    if len(agenda_result.docs) == 0:
        return (
            flask.jsonify({"error": gettext("%(section)s item not found", section=app.config["AGENDA_SECTION"])}),
            404,
        )

    if restrict_coverage_info(get_company()):
        remove_restricted_coverage_info([agenda_result.docs[0]])

    wire_ids = []
    for cov in agenda_result.docs[0].get("coverages") or []:
        if cov.get("coverage_type") == "text" and cov.get("delivery_id"):
            wire_ids.append(cov["delivery_id"])

    wire_items = get_entities_elastic_or_mongo_or_404(wire_ids, "items")
    aggregations = {"ids": {"terms": {"field": "_id"}}}
    permissioned_result = get_resource_service("wire_search").get_items(
        wire_ids, size=0, aggregations=aggregations, apply_permissions=True
    )
    buckets = permissioned_result.hits["aggregations"]["ids"]["buckets"]
    permissioned_ids = []
    for b in buckets:
        permissioned_ids.append(b["key"])

    for wire_item in wire_items:
        set_item_permission(wire_item, wire_item.get("_id") in permissioned_ids)

    return (
        flask.jsonify(
            {
                "agenda_item": agenda_result.docs[0],
                "wire_items": wire_items,
            }
        ),
        200,
    )


@blueprint.route("/agenda/search_locations")
@login_required
def search_locations():
    query = request.args.get("q") or ""
    apply_filters = len(query) > 0

    if apply_filters and not query.startswith("*") and not query.endswith("*"):
        query = f"*{query}*"

    def gen_agg_filter(field: str):
        return {
            "bool": {
                "filter": [
                    {
                        "query_string": {
                            "fields": [f"location.{field}"],
                            "query": query,
                        },
                    }
                ],
            },
        }

    def gen_agg_terms(field: str):
        return {
            "field": f"location.{field}.keyword",
            "size": 1000,
        }

    es_query = {
        "size": 0,
        "aggs": {
            "city_search_country": {
                "terms": gen_agg_terms("address.country"),
                "aggs": {
                    "city_search_state": {
                        "terms": gen_agg_terms("address.state"),
                        "aggs": {
                            "cities": {
                                "terms": gen_agg_terms("address.city"),
                            },
                        },
                    },
                },
            },
            "state_search_country": {
                "terms": gen_agg_terms("address.country"),
                "aggs": {
                    "states": {
                        "terms": gen_agg_terms("address.state"),
                    },
                },
            },
            "countries": {
                "terms": gen_agg_terms("address.country"),
            },
            "places": {"terms": gen_agg_terms("name")},
        },
    }

    if apply_filters:
        es_query["query"] = {
            "bool": {
                "filter": [
                    {
                        "query_string": {
                            "fields": [
                                "location.address.city",
                                "location.address.state",
                                "location.address.country",
                                "location.name",
                            ],
                            "query": query,
                        },
                    }
                ],
            },
        }

        es_query["aggs"]["city_search"] = {
            "filter": gen_agg_filter("address.city"),
            "aggs": {"city_search_country": es_query["aggs"].pop("city_search_country")},
        }
        es_query["aggs"]["state_search"] = {
            "filter": gen_agg_filter("address.state"),
            "aggs": {"state_search_country": es_query["aggs"].pop("state_search_country")},
        }
        es_query["aggs"]["country_search"] = {
            "filter": gen_agg_filter("address.country"),
            "aggs": {"countries": es_query["aggs"].pop("countries")},
        }
        es_query["aggs"]["place_search"] = {
            "filter": gen_agg_filter("name"),
            "aggs": {"places": es_query["aggs"].pop("places")},
        }

    req = ParsedRequest()
    req.args = {"source": json.dumps(es_query)}
    service = get_resource_service("agenda")
    cursor = service.internal_get(req, {})
    aggs = cursor.hits.get("aggregations") or {}

    regions = []
    for country_bucket in (aggs.get("city_search_country") or aggs["city_search"]["city_search_country"])["buckets"]:
        country_name = country_bucket["key"]
        for state_bucket in country_bucket["city_search_state"]["buckets"]:
            state_name = state_bucket["key"]
            for city_bucket in state_bucket["cities"]["buckets"]:
                regions.append(
                    {"name": city_bucket["key"], "country": country_name, "state": state_name, "type": "city"}
                )

    for country_bucket in (aggs.get("state_search_country") or aggs["state_search"]["state_search_country"])["buckets"]:
        country_name = country_bucket["key"]
        for state_bucket in country_bucket["states"]["buckets"]:
            regions.append(
                {
                    "name": state_bucket["key"],
                    "country": country_name,
                    "type": "state",
                }
            )

    for country_bucket in (aggs.get("countries") or aggs["country_search"]["countries"])["buckets"]:
        regions.append(
            {
                "name": country_bucket["key"],
                "type": "country",
            }
        )

    return (
        {
            "regions": regions,
            "places": [bucket["key"] for bucket in (aggs.get("places") or aggs["place_search"]["places"])["buckets"]],
        },
        200,
    )
