import hmac
import flask
import logging

import newsroom.signals as signals
from copy import copy, deepcopy
from datetime import datetime
from typing import Optional, Set

from flask import current_app as app
from flask_babel import gettext
from bson import ObjectId
import superdesk
from superdesk.text_utils import get_word_count, get_char_count
from superdesk.utc import utcnow
from superdesk.errors import SuperdeskApiError
from planning.common import WORKFLOW_STATE
from newsroom.celery_app import celery

from newsroom.notifications import (
    push_notification,
    save_user_notifications,
    UserNotification,
)
from newsroom.topics.topics import (
    get_agenda_notification_topics_for_query_by_id,
    get_topics_with_subscribers,
)
from newsroom.utils import parse_dates, get_user_dict, get_company_dict, parse_date_str
from newsroom.email import (
    send_new_item_notification_email,
    send_history_match_notification_email,
    send_item_killed_notification_email,
)
from newsroom.history import get_history_users
from newsroom.wire.views import delete_dashboard_caches
from newsroom.wire import url_for_wire
from newsroom.upload import ASSETS_RESOURCE
from newsroom.agenda.utils import (
    get_latest_available_delivery,
    TO_BE_CONFIRMED_FIELD,
    push_agenda_item_notification,
)


logger = logging.getLogger(__name__)
blueprint = flask.Blueprint("push", __name__)

KEY = "PUSH_KEY"


def test_signature(request):
    """Test if request is signed using app PUSH_KEY."""
    if not app.config.get(KEY):
        if not app.config.get("TESTING"):
            logger.warning("PUSH_KEY is not configured, can not verify incoming data.")
        return True
    payload = request.get_data()
    key = app.config[KEY]
    mac = hmac.new(key, payload, "sha1")
    return hmac.compare_digest(request.headers.get("x-superdesk-signature", ""), "sha1=%s" % mac.hexdigest())


def assert_test_signature(request):
    if not test_signature(request):
        logger.warning("signature invalid on push from %s", request.referrer or request.remote_addr)
        flask.abort(403)


def fix_hrefs(doc):
    if doc.get("renditions"):
        for key, rendition in doc["renditions"].items():
            if rendition.get("media"):
                rendition["href"] = app.upload_url(rendition["media"])
    for assoc in doc.get("associations", {}).values():
        fix_hrefs(assoc)


@blueprint.route("/push", methods=["POST"])
def push():
    assert_test_signature(flask.request)
    item = flask.json.loads(flask.request.get_data())
    assert "guid" in item or "_id" in item, {"guid": 1}
    assert "type" in item, {"type": 1}

    signals.push.send(app._get_current_object(), item=item)

    if item.get("type") == "event":
        orig = app.data.find_one("agenda", req=None, guid=item["guid"])
        _id = publish_event(item, orig)
        notify_new_agenda_item.delay(_id, check_topics=True)
    elif item.get("type") == "planning":
        orig = app.data.find_one("agenda", req=None, guid=item["guid"]) or {}
        item["planning_date"] = parse_date_str(item["planning_date"])
        plan_id = publish_planning_item(item, orig)
        event_id = publish_planning_into_event(item)
        # Prefer parent Event when sending notificaitons
        _id = event_id or plan_id
        notify_new_agenda_item.delay(_id, check_topics=True)
    elif item.get("type") == "text":
        orig = superdesk.get_resource_service("items").find_one(req=None, _id=item["guid"])
        item["_id"] = publish_item(item, orig)
        notify_new_wire_item.delay(
            item["_id"], check_topics=orig is None or app.config["WIRE_NOTIFICATIONS_ON_CORRECTIONS"]
        )
    elif item["type"] == "planning_featured":
        publish_planning_featured(item)
    else:
        flask.abort(400, gettext("Unknown type {}".format(item.get("type"))))

    if app.config.get("DELETE_DASHBOARD_CACHE_ON_PUSH", True):
        delete_dashboard_caches()
    return flask.jsonify({})


def set_dates(doc):
    now = utcnow()
    parse_dates(doc)
    doc.setdefault("firstcreated", now)
    doc.setdefault("versioncreated", now)
    doc.setdefault("version", 1)
    doc.setdefault(app.config["VERSION"], 1)


def publish_item(doc, original):
    """Duplicating the logic from content_api.publish service."""
    set_dates(doc)
    doc["firstpublished"] = parse_date_str(doc.get("firstpublished"))
    doc["publish_schedule"] = parse_date_str(doc.get("publish_schedule"))
    doc.setdefault("wordcount", get_word_count(doc.get("body_html", "")))
    doc.setdefault("charcount", get_char_count(doc.get("body_html", "")))
    doc["original_id"] = doc["guid"]

    service = superdesk.get_resource_service("content_api")
    service.datasource = "items"

    if doc.get("evolvedfrom"):
        parent_item = service.find_one(req=None, _id=doc["evolvedfrom"])
        if parent_item:
            if parent_item.get("original_id"):
                doc["original_id"] = parent_item["original_id"]
            doc["ancestors"] = copy(parent_item.get("ancestors", []))
            doc["ancestors"].append(doc["evolvedfrom"])
            doc["bookmarks"] = parent_item.get("bookmarks", [])
            doc["planning_id"] = parent_item.get("planning_id")
            doc["coverage_id"] = parent_item.get("coverage_id")
        else:
            logger.warning(
                "Failed to find evolvedfrom item %s for %s",
                doc["evolvedfrom"],
                doc["guid"],
            )

    fix_hrefs(doc)
    logger.debug("publishing %s", doc["guid"])
    for assoc in doc.get("associations", {}).values():
        if assoc:
            assoc.setdefault("subscribers", [])
            app.generate_renditions(assoc)

    # If there is a function defined that generates renditions for embedded images call it.
    if app.generate_embed_renditions:
        app.generate_embed_renditions(doc)

    try:
        if doc.get("coverage_id"):
            agenda_items = superdesk.get_resource_service("agenda").set_delivery(doc)
            if agenda_items:
                [notify_new_agenda_item.delay(item["_id"], check_topics=False) for item in agenda_items]
    except Exception as ex:
        logger.info("Failed to notify new wire item for Agenda watches")
        logger.exception(ex)

    if app.config.get("WIRE_SUBJECT_SCHEME_WHITELIST") and doc.get("subject"):
        doc["subject"] = [
            subject
            for subject in doc["subject"]
            if subject.get("scheme") in app.config["WIRE_SUBJECT_SCHEME_WHITELIST"]
        ]

    signals.publish_item.send(app._get_current_object(), item=doc, is_new=original is None)
    _id = service.create([doc])[0]
    if "associations" not in doc and original is not None and bool(original.get("associations", {})):
        service.patch(_id, updates={"associations": None})
    if "evolvedfrom" in doc and parent_item:
        service.system_update(parent_item["_id"], {"nextversion": _id}, parent_item)
    return _id


def publish_event(event, orig):
    logger.debug("publishing event %s", event)
    validate_event_push(orig, event)

    # populate attachments href
    if event.get("files"):
        for file_ref in event["files"]:
            if file_ref.get("media"):
                file_ref.setdefault("href", app.upload_url(file_ref["media"]))

    _id = event["guid"]
    service = superdesk.get_resource_service("agenda")

    plan_ids = event.pop("plans", [])

    if not orig:
        # new event
        agenda = {}
        set_agenda_metadata_from_event(agenda, event)
        agenda["dates"] = get_event_dates(event)

        # Retrieve all current Planning items and add them into this Event
        agenda.setdefault("planning_items", [])
        for plan in service.find(where={"_id": {"$in": plan_ids}}):
            planning_item = plan["planning_items"][0]
            agenda["planning_items"].append(planning_item)
            set_agenda_planning_items(agenda, orig, planning_item, action="add", send_notification=False)

            if not plan.get("event_id"):
                # Make sure the Planning item has an ``event_id`` defined
                # This can happen when pushing a Planning item before linking to an Event
                service.system_update(plan["_id"], {"event_id": _id}, plan)

        _id = service.post([agenda])[0]
    else:
        # replace the original document
        updates = None
        if (
            event.get("state") in [WORKFLOW_STATE.CANCELLED, WORKFLOW_STATE.KILLED]
            or event.get("pubstatus") == "cancelled"
        ):
            # it has been cancelled so don't need to change the dates
            # update the event, the version and the state
            updates = {
                "event": event,
                "version": event.get("version", event.get(app.config["VERSION"])),
                "state": event["state"],
                "state_reason": event.get("state_reason"),
                "planning_items": orig.get("planning_items"),
                "coverages": orig.get("coverages"),
            }

            if event.get("pubstatus") == "cancelled":
                # item removed, reset watches on the item
                updates["watches"] = []

        elif event.get("state") in [
            WORKFLOW_STATE.RESCHEDULED,
            WORKFLOW_STATE.POSTPONED,
        ]:
            # schedule is changed, recalculate the dates, planning id and coverages from dates will be removed
            updates = {}
            set_agenda_metadata_from_event(updates, event, False)
            updates["dates"] = get_event_dates(event)
            updates["coverages"] = None
            updates["planning_items"] = None

        elif event.get("state") == WORKFLOW_STATE.SCHEDULED:
            # event is reposted (possibly after a cancel)
            updates = {
                "event": event,
                "version": event.get("version", event.get(app.config["VERSION"])),
                "state": event["state"],
                "dates": get_event_dates(event),
                "planning_items": orig.get("planning_items"),
                "coverages": orig.get("coverages"),
            }

            set_agenda_metadata_from_event(updates, event, False)

        if updates:
            service.patch(orig["_id"], updates)
            updates["_id"] = orig["_id"]
            superdesk.get_resource_service("agenda").notify_agenda_update(updates, orig)

    return _id


def get_event_dates(event):
    if not isinstance(event["dates"]["start"], datetime):
        event["dates"]["start"] = datetime.strptime(event["dates"]["start"], "%Y-%m-%dT%H:%M:%S+0000")
    if not isinstance(event["dates"]["end"], datetime):
        event["dates"]["end"] = datetime.strptime(event["dates"]["end"], "%Y-%m-%dT%H:%M:%S+0000")
    event["dates"].setdefault("all_day", False)
    event["dates"].setdefault("no_end_time", False)
    return event["dates"]


def validate_event_push(orig, updates):
    event = deepcopy(orig or {})
    event.update(updates)
    dates = get_event_dates(event)
    event_id = event.get("guid")

    max_duration = app.config["MAX_MULTI_DAY_EVENT_DURATION"] or 365
    if (dates["end"] - dates["start"]).days > max_duration:
        raise SuperdeskApiError.badRequestError(
            f"Failed to ingest Event with id '{event_id}': duration exceeds maximum allowed"
        )


def publish_planning_item(planning, orig):
    service = superdesk.get_resource_service("agenda")
    agenda = deepcopy(orig)

    init_adhoc_agenda(planning, agenda)

    # Update agenda metadata
    new_plan = set_agenda_metadata_from_planning(agenda, planning, force_adhoc=True)

    # Add the planning item to the list
    set_agenda_planning_items(agenda, orig, planning, action="add" if new_plan else "update")

    if not agenda.get("_id"):
        # Setting ``_id`` of Agenda to be equal to the Planning item if there's no Event ID
        agenda.setdefault("_id", planning["guid"])
        agenda.setdefault("guid", planning["guid"])
        return service.post([agenda])[0]
    else:
        # Replace the original
        service.patch(agenda["_id"], agenda)
        return agenda["_id"]


def publish_planning_into_event(planning) -> Optional[str]:
    if not planning.get("event_item"):
        return None

    service = superdesk.get_resource_service("agenda")

    event_id = planning["event_item"]
    plan_id = planning["guid"]
    orig_agenda = service.find_one(req=None, _id=event_id)

    if not orig_agenda:
        # Item not found using ``event_item`` attribute
        # Try again using ``guid`` attribute
        orig_agenda = service.find_one(req=None, _id=plan_id)

    if (orig_agenda or {}).get("item_type") != "event":
        # event id exists in planning item but event is not in the system
        logger.warning(f"Event '{event_id}' for Planning '{plan_id}' not found")
        return None

    agenda = deepcopy(orig_agenda)

    if (
        planning.get("state") in [WORKFLOW_STATE.CANCELLED, WORKFLOW_STATE.KILLED]
        or planning.get("pubstatus") == "cancelled"
    ):
        # Remove the Planning item from the list
        set_agenda_planning_items(agenda, orig_agenda, planning, action="remove")
        service.patch(agenda["_id"], agenda)
        return None

    # Update agenda metadata
    new_plan = set_agenda_metadata_from_planning(agenda, planning)

    # Add the Planning item to the list
    set_agenda_planning_items(agenda, orig_agenda, planning, action="add" if new_plan else "update")

    if not agenda.get("_id"):
        # setting _id of agenda to be equal to planning if there's no event id
        agenda.setdefault("_id", planning.get("event_item", planning["guid"]) or planning["guid"])
        agenda.setdefault("guid", planning.get("event_item", planning["guid"]) or planning["guid"])
        return service.post([agenda])[0]
    else:
        # Replace the original document
        service.patch(agenda["_id"], agenda)
        return agenda["_id"]


def init_adhoc_agenda(planning, agenda):
    """
    Inits an adhoc agenda item
    """

    # check if there's an existing ad-hoc

    agenda["item_type"] = "planning"

    # planning dates is saved as the dates of the new agenda
    agenda["dates"] = {
        "start": planning["planning_date"],
        "end": planning["planning_date"],
    }

    agenda["state"] = planning["state"]
    if planning.get("pubstatus") == "cancelled":
        agenda["watches"] = []

    return agenda


def set_agenda_metadata_from_event(agenda, event, set_doc_id=True):
    """
    Sets agenda metadata from a given event
    """
    parse_dates(event)

    # setting _id of agenda to be equal to event
    if set_doc_id:
        agenda.setdefault("_id", event["guid"])

    agenda["item_type"] = "event"
    agenda["guid"] = event["guid"]
    agenda["event_id"] = event["guid"]
    agenda["recurrence_id"] = event.get("recurrence_id")
    agenda["name"] = event.get("name")
    agenda["slugline"] = event.get("slugline")
    agenda["definition_short"] = event.get("definition_short")
    agenda["definition_long"] = event.get("definition_long")
    agenda["version"] = event.get("version")
    agenda["calendars"] = event.get("calendars")
    agenda["location"] = event.get("location")
    agenda["ednote"] = event.get("ednote")
    agenda["state"] = event.get("state")
    agenda["state_reason"] = event.get("state_reason")
    agenda["place"] = event.get("place")
    agenda["subject"] = format_qcode_items(event.get("subject"))
    agenda["products"] = event.get("products")
    agenda["service"] = format_qcode_items(event.get("anpa_category"))
    agenda["event"] = event
    agenda["registration_details"] = event.get("registration_details")
    agenda["invitation_details"] = event.get("invitation_details")
    agenda["language"] = event.get("language")
    agenda["source"] = event.get("source")

    set_dates(agenda)


def format_qcode_items(items=None):
    if not items:
        return []

    for item in items:
        item["code"] = item.get("qcode")

    return items


def set_agenda_metadata_from_planning(agenda, planning_item, force_adhoc=False):
    """Sets agenda metadata from a given planning"""

    parse_dates(planning_item)
    set_dates(agenda)

    if not planning_item.get("event_item") or force_adhoc:
        # adhoc planning item
        agenda["name"] = planning_item.get("name")
        agenda["headline"] = planning_item.get("headline")
        agenda["slugline"] = planning_item.get("slugline")
        agenda["ednote"] = planning_item.get("ednote")
        agenda["place"] = planning_item.get("place")
        agenda["subject"] = format_qcode_items(planning_item.get("subject"))
        agenda["products"] = planning_item.get("products")
        agenda["urgency"] = planning_item.get("urgency")
        agenda["definition_short"] = planning_item.get("description_text") or agenda.get("definition_short")
        agenda["definition_long"] = planning_item.get("abstract") or agenda.get("definition_long")
        agenda["service"] = format_qcode_items(planning_item.get("anpa_category"))
        agenda["state"] = planning_item.get("state")
        agenda["state_reason"] = planning_item.get("state_reason")
        agenda["language"] = planning_item.get("language")
        agenda["source"] = planning_item.get("source")

    if planning_item.get("event_item") and force_adhoc:
        agenda["event_id"] = planning_item["event_item"]

    if not agenda.get("planning_items"):
        agenda["planning_items"] = []

    new_plan = False
    plan = next(
        (p for p in (agenda.get("planning_items")) if p.get("guid") == planning_item.get("guid")),
        {},
    )

    if not plan:
        new_plan = True

    plan["_id"] = planning_item.get("_id") or planning_item.get("guid")
    plan["guid"] = planning_item.get("guid")
    plan["slugline"] = planning_item.get("slugline")
    plan["description_text"] = planning_item.get("description_text")
    plan["headline"] = planning_item.get("headline")
    plan["name"] = planning_item.get("name")
    plan["abstract"] = planning_item.get("abstract")
    plan["place"] = planning_item.get("place")
    plan["subject"] = format_qcode_items(planning_item.get("subject"))
    plan["service"] = format_qcode_items(planning_item.get("anpa_category"))
    plan["urgency"] = planning_item.get("urgency")
    plan["planning_date"] = planning_item.get("planning_date")
    plan["coverages"] = planning_item.get("coverages") or []
    plan["ednote"] = planning_item.get("ednote")
    plan["internal_note"] = planning_item.get("internal_note")
    plan["versioncreated"] = parse_date_str(planning_item.get("versioncreated"))
    plan["firstcreated"] = parse_date_str(planning_item.get("firstcreated"))
    plan["state"] = planning_item.get("state")
    plan["state_reason"] = planning_item.get("state_reason")
    plan["products"] = planning_item.get("products")
    plan["agendas"] = planning_item.get("agendas")
    plan[TO_BE_CONFIRMED_FIELD] = planning_item.get(TO_BE_CONFIRMED_FIELD)
    plan["language"] = planning_item.get("language")
    plan["source"] = planning_item.get("source")

    if new_plan:
        agenda["planning_items"].append(plan)

    return new_plan


def set_agenda_planning_items(agenda, orig_agenda, planning_item, action="add", send_notification=True):
    """
    Updates the list of planning items of agenda. If action is 'add' then adds the new one.
    And updates the list of coverages
    """

    if action == "remove":
        existing_planning_items = agenda.get("planning_items") or []
        agenda["planning_items"] = [p for p in existing_planning_items if p["guid"] != planning_item["guid"]] or []
        if (
            len(agenda["planning_items"]) < len(existing_planning_items)
            and len(planning_item.get("coverages") or []) > 0
        ):
            superdesk.get_resource_service("agenda").notify_agenda_update(
                agenda, orig_agenda, planning_item, True, planning_item
            )

    agenda["coverages"], coverage_changes = get_coverages(
        agenda["planning_items"],
        (orig_agenda or {}).get("coverages") or [],
        planning_item if action == "add" else None,
    )

    if (
        send_notification
        and action != "remove"
        and (
            coverage_changes.get("coverage_added")
            or coverage_changes.get("coverage_cancelled")
            or coverage_changes.get("coverage_modified")
        )
    ):
        superdesk.get_resource_service("agenda").notify_agenda_update(agenda, orig_agenda, planning_item, True)

    agenda["display_dates"] = get_display_dates(agenda["dates"], agenda["planning_items"])
    agenda.pop("_updated", None)


def get_display_dates(agenda_date, planning_items):
    """
    Returns the list of dates where a planning item or a coverage falls outside
    of the agenda item dates
    """
    display_dates = []

    for planning_item in planning_items:
        if not planning_item.get("coverages"):
            parsed_date = parse_date_str(planning_item["planning_date"])
            display_dates.append({"date": parsed_date})

        for coverage in planning_item.get("coverages") or []:
            parsed_date = parse_date_str(coverage["planning"]["scheduled"])
            display_dates.append({"date": parsed_date})

    return display_dates


def get_coverages(planning_items, original_coverages, new_plan):
    """
    Returns list of coverages for given planning items
    """

    def get_existing_coverage(id):
        return next((o for o in original_coverages if o["coverage_id"] == id), {})

    def set_delivery(coverage, deliveries, orig_coverage=None):
        cov_deliveries = []
        if coverage["coverage_type"] == "text":
            for d in deliveries or []:
                cov_deliveries.append(
                    {
                        "delivery_id": d.get("item_id"),
                        "delivery_href": url_for_wire(
                            None,
                            _external=False,
                            section="wire.item",
                            _id=d.get("item_id"),
                        ),
                        "delivery_state": d.get("item_state"),
                        "sequence_no": d.get("sequence_no") or 0,
                        "publish_time": parse_date_str(d.get("publish_time")),
                    }
                )
        else:
            if coverage.get("workflow_status") == "completed":
                if orig_coverage.get("workflow_status") != coverage["workflow_status"]:
                    cov_deliveries.append(
                        {
                            "sequence_no": 0,
                            "delivery_state": "published",
                            "publish_time": (
                                next(
                                    (parse_date_str(d.get("publish_time")) for d in deliveries),
                                    None,
                                )
                                or utcnow()
                            ),
                        }
                    )

                    try:
                        cov_deliveries[0]["delivery_href"] = app.set_photo_coverage_href(
                            coverage, planning_item, cov_deliveries
                        )
                    except Exception as e:
                        logger.exception(e)
                        logger.error(
                            "Failed to generate delivery_href for coverage={}".format(coverage.get("coverage_id"))
                        )
                elif len((orig_coverage or {}).get("deliveries") or []) > 0:
                    cov_deliveries.append(orig_coverage["deliveries"][0])

        coverage["deliveries"] = cov_deliveries
        # Sort the deliveries in reverse sequence order here, so sorting required anywhere else
        coverage["deliveries"].sort(key=lambda d: d["sequence_no"], reverse=True)

        # Get latest delivery that was 'published'
        latest_available_delivery = get_latest_available_delivery(coverage) or {}
        coverage["delivery_id"] = latest_available_delivery.get("delivery_id")
        coverage["delivery_href"] = latest_available_delivery.get("delivery_href")
        coverage["publish_time"] = latest_available_delivery.get("publish_time")

    coverages = []
    coverage_changes = {}
    for planning_item in planning_items:
        if planning_item.get("state") != WORKFLOW_STATE.KILLED:
            for coverage in planning_item.get("coverages") or []:
                existing_coverage = get_existing_coverage(coverage["coverage_id"])
                coverage_planning = coverage.get("planning") or {}

                new_coverage = {
                    "planning_id": planning_item.get("guid"),
                    "coverage_id": coverage.get("coverage_id"),
                    "scheduled": coverage_planning.get("scheduled"),
                    "coverage_type": coverage_planning.get("g2_content_type"),
                    "workflow_status": coverage.get("workflow_status"),
                    "coverage_status": coverage.get("news_coverage_status", {}).get("name"),
                    "slugline": coverage_planning.get("slugline"),
                    "genre": coverage_planning.get("genre", []),
                    "coverage_provider": (coverage.get("coverage_provider") or {}).get("name"),
                    "watches": existing_coverage.get("watches") or coverage.get("watches", []),
                }

                if TO_BE_CONFIRMED_FIELD in coverage:
                    new_coverage[TO_BE_CONFIRMED_FIELD] = coverage[TO_BE_CONFIRMED_FIELD]

                set_delivery(new_coverage, coverage.get("deliveries"), existing_coverage)
                coverages.append(new_coverage)

                if (coverage and not existing_coverage) or ((new_plan or {}).get("_id")) == planning_item.get("_id"):
                    coverage_changes["coverage_added"] = True
                else:
                    if coverage["workflow_status"] != existing_coverage["workflow_status"]:
                        if coverage.get("workflow_status") in [
                            WORKFLOW_STATE.CANCELLED,
                            WORKFLOW_STATE.DRAFT,
                        ]:
                            coverage_changes["coverage_cancelled"] = True

                        if new_coverage.get("workflow_status") == "completed":
                            coverage_changes["coverage_modified"] = True
                            set_item_reference(new_coverage)

                    if (
                        existing_coverage.get("scheduled") != new_coverage.get("scheduled")
                        and existing_coverage.get("workflow_status") != "completed"
                    ):
                        coverage_changes["coverage_modified"] = True

    if len(original_coverages or []) > len(coverages):
        coverage_changes["coverage_cancelled"] = True

    return coverages, coverage_changes


def set_item_reference(coverage):
    """
    Check if the delivery in the passed coverage refers back to the agenda item and coverage.
    If the item is fulfilled after the item is published it will not have this reference
    :param coverage:
    :return:
    """
    if coverage.get("delivery_id") is None:
        return
    item = superdesk.get_resource_service("items").find_one(req=None, _id=coverage.get("delivery_id"))
    if item:
        if "planning_id" not in item and "coverage_id" not in item:
            service = superdesk.get_resource_service("content_api")
            service.datasource = "items"
            service.patch(
                item.get("_id"),
                updates={
                    "planning_id": coverage.get("planning_id"),
                    "coverage_id": coverage.get("coverage_id"),
                },
            )
            item["planning_id"] = coverage.get("planning_id")
            item["coverage_id"] = coverage.get("coverage_id")
            notify_new_wire_item.delay(item["_id"], check_topics=False)


@celery.task
def notify_new_wire_item(_id, check_topics=True):
    item = superdesk.get_resource_service("items").find_one(req=None, _id=_id)
    if item:
        notify_new_item(item, check_topics=check_topics)


@celery.task
def notify_new_agenda_item(_id, check_topics=True):
    agenda = app.data.find_one("agenda", req=None, _id=_id)
    if agenda:
        superdesk.get_resource_service("agenda").enhance_items([agenda])
        notify_new_item(agenda, check_topics=check_topics)


def notify_new_item(item, check_topics=True):
    if not item or item.get("type") == "composite":
        return

    item_type = item.get("type")
    users_with_realtime_subscription: Set[ObjectId] = set()
    try:
        user_dict = get_user_dict()
        user_ids = [u["_id"] for u in user_dict.values()]

        company_dict = get_company_dict()
        company_ids = [c["_id"] for c in company_dict.values()]

        if item_type == "agenda":
            push_agenda_item_notification("new_item", item=item)
        else:
            push_notification("new_item", _items=[item])

        if check_topics:
            if item_type == "text":
                users_with_realtime_subscription = notify_wire_topic_matches(item, user_dict, company_dict)
            else:
                users_with_realtime_subscription = notify_agenda_topic_matches(item, user_dict, company_dict)

        notify_user_matches(
            item,
            user_dict,
            company_dict,
            user_ids,
            company_ids,
            users_with_realtime_subscription
            if not item.get("pubstatus", item.get("state")) in ["canceled", "cancelled"]
            else set(),
        )
    except Exception as e:
        logger.exception(e)
        logger.error(f"Failed to notify users for new {item_type} item", extra={"_id": item["_id"]})


def notify_user_matches(item, users_dict, companies_dict, user_ids, company_ids, users_with_realtime_subscription):
    """Send notification to users who have downloaded or bookmarked the provided item"""

    related_items = item.get("ancestors", [])
    related_items.append(item["_id"])
    is_text = item.get("type") == "text"

    users_processed = []

    def _get_users(section):
        """Get the list of users who have downloaded or bookmarked the items"""
        # Get users who have downloaded any of the items
        user_list = get_history_users(related_items, user_ids, company_ids, section, "download")

        if is_text and section != "agenda":
            # Add users who have bookmarked any of the items
            service = superdesk.get_resource_service("{}_search".format(section))
            bookmarked_users = service.get_matching_bookmarks(related_items, users_dict, companies_dict)

            user_list.extend(bookmarked_users)

        # Add users if this section is wire
        # Or if the user is not already in the list of users for wire
        user_list = [
            user_id
            for user_id in user_list
            if user_id not in users_processed and ObjectId(user_id) not in users_with_realtime_subscription
        ]

        users_processed.extend(user_list)

        # Remove duplicates and return the list
        return list(set(user_list))

    def _send_notification(section, users_ids):
        if not users_ids:
            return

        save_user_notifications(
            [
                UserNotification(
                    user=user,
                    item=item["_id"],
                    resource=item.get("type"),
                    action="history_match",
                    data=None,
                )
                for user in users_ids
            ]
        )

        send_user_notification_emails(item, users_ids, users_dict, section)

    # First add users for the 'wire' section and send the notification
    # As this takes precedence over all other sections
    # (in case items appear in multiple sections)
    _send_notification("wire", _get_users("wire"))

    # Next iterate over the registered sections (excluding wire and api)
    for section_id in [
        section["_id"]
        for section in app.sections
        if section["_id"] != "wire" and section["group"] not in ["api", "monitoring"]
    ]:
        # Add the users for those sections and send the notification
        _send_notification(section_id, _get_users(section_id))


def send_user_notification_emails(item, user_matches, users, section):
    for user_id in user_matches:
        user = users.get(str(user_id))
        if item.get("pubstatus", item.get("state")) in ["canceled", "cancelled"]:
            send_item_killed_notification_email(user, item=item)
        else:
            if user.get("receive_email"):
                send_history_match_notification_email(user, item=item, section=section)


def notify_wire_topic_matches(item, users_dict, companies_dict) -> Set[ObjectId]:
    topics = get_topics_with_subscribers("wire")
    topic_matches = superdesk.get_resource_service("wire_search").get_matching_topics(
        item["_id"], topics, users_dict, companies_dict
    )

    if topic_matches:
        push_notification("topic_matches", item=item, topics=topic_matches)
        return send_topic_notification_emails(item, topics, topic_matches, users_dict, companies_dict)
    else:
        return set()


def notify_agenda_topic_matches(item, users_dict, companies_dict) -> Set[ObjectId]:
    topics = get_topics_with_subscribers("agenda")
    topic_matches = superdesk.get_resource_service("agenda").get_matching_topics(
        item["_id"], topics, users_dict, companies_dict
    )

    # Include topics where the ``query`` is ``item["_id"]``
    topic_matches.extend(
        [
            topic
            for topic in get_agenda_notification_topics_for_query_by_id(item, users_dict)
            if topic.get("_id") not in topic_matches
        ]
    )

    if topic_matches:
        push_agenda_item_notification("topic_matches", item=item, topics=topic_matches)
        return send_topic_notification_emails(item, topics, topic_matches, users_dict, companies_dict)
    else:
        return set()


def send_topic_notification_emails(item, topics, topic_matches, users, companies) -> Set[ObjectId]:
    users_processed: Set[ObjectId] = set()
    users_with_realtime_subscription: Set[ObjectId] = set()

    for topic in topics:
        if topic["_id"] not in topic_matches:
            continue

        for subscriber in topic.get("subscribers") or []:
            user = users.get(str(subscriber["user_id"]))

            if not user:
                continue

            company = companies.get(str(user.get("company")))

            section = topic.get("topic_type") or "wire"
            if user["_id"] not in users_processed:
                # Only send websocket notification once for each item
                save_user_notifications(
                    [
                        UserNotification(
                            user=user["_id"],
                            item=item["_id"],
                            resource=section,
                            action="topic_matches",
                            data=None,
                        )
                    ]
                )
                users_processed.add(user["_id"])

            if not user.get("receive_email"):
                continue
            elif subscriber.get("notification_type") == "scheduled":
                superdesk.get_resource_service("notification_queue").add_item_to_queue(
                    user["_id"], section, topic["_id"], item
                )
            elif user["_id"] in users_with_realtime_subscription:
                # This user has already received a realtime notification email about this item
                # No need to send another
                continue
            else:
                users_with_realtime_subscription.add(user["_id"])
                search_service = superdesk.get_resource_service(
                    "wire_search" if topic["topic_type"] == "wire" else "agenda"
                )
                query = search_service.get_topic_query(
                    topic, user, company, args={"es_highlight": 1, "ids": [item["_id"]]}
                )

                items = search_service.get_items_by_query(query, size=1)
                highlighted_item = item
                if items.count():
                    highlighted_item = items[0]

                send_new_item_notification_email(
                    user,
                    topic["label"],
                    item=highlighted_item,
                    section=section,
                )

    return users_with_realtime_subscription


# keeping this for testing
@blueprint.route("/notify", methods=["POST"])
def notify():
    data = flask.json.loads(flask.request.get_data())
    notify_new_item(data["item"])
    return flask.jsonify({"status": "OK"}), 200


@blueprint.route("/push_binary", methods=["POST"])
def push_binary():
    assert_test_signature(flask.request)
    media = flask.request.files["media"]
    media_id = flask.request.form["media_id"]
    app.media.put(media, resource=ASSETS_RESOURCE, _id=media_id, content_type=media.content_type)
    return flask.jsonify({"status": "OK"}), 201


@blueprint.route("/push_binary/<media_id>")
def push_binary_get(media_id):
    if app.media.get(media_id, resource=ASSETS_RESOURCE):
        return flask.jsonify({})
    else:
        flask.abort(404)


def publish_planning_featured(item):
    assert item.get("_id"), {"_id": 1}
    service = superdesk.get_resource_service("agenda_featured")
    orig = service.find_one(req=None, _id=item["_id"])
    if orig:
        service.update(orig["_id"], {"items": item.get("items") or []}, orig)
    else:
        # Assert `tz` and `items` in initial push only
        assert item.get("tz"), {"tz": 1}
        assert item.get("items"), {"items": 1}
        service.create([item])
