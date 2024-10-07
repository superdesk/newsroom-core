import hmac
import logging

from typing import Any
from copy import deepcopy
from datetime import datetime

from superdesk.utc import utcnow
from superdesk.types import Item
from superdesk.core.web import Request
from superdesk.core import get_app_config
from superdesk import get_resource_service
from superdesk.errors import SuperdeskApiError
from superdesk.resource_fields import VERSION

from newsroom.utils import parse_date_str, parse_dates
from newsroom.core import get_current_wsgi_app


logger = logging.getLogger(__name__)

KEY = "PUSH_KEY"


def set_dates(doc: dict[str, Any]):
    now = utcnow()
    parse_dates(doc)
    doc.setdefault("firstcreated", now)
    doc.setdefault("versioncreated", now)
    doc.setdefault("version", 1)
    doc.setdefault(VERSION, 1)


def fix_updates(doc: dict[str, Any], next_item: Item):
    service = get_resource_service("content_api")
    ancestors = (doc.get("ancestors") or []) + [doc["guid"]]

    for i in range(50):
        updates = {"ancestors": ancestors + (next_item.get("ancestors") or []), "original_id": doc["original_id"]}
        service.system_update(next_item["_id"], updates, next_item)
        next_item = service.find_one(req=None, evolvedfrom=next_item["_id"])
        if next_item is None:
            break
    else:
        logger.warning("Didn't fix ancestors in 50 iterations", extra={"guid": doc["guid"]})


def format_qcode_items(items: list[dict[str, Any]] | None = None):
    if not items:
        return []

    for item in items:
        item["code"] = item.get("qcode")

    return items


def get_display_dates(planning_items: list[dict[str, Any]]):
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


def validate_event_push(orig: dict[str, Any], updates: dict[str, Any]):
    event = deepcopy(orig or {})
    event.update(updates)
    dates = get_event_dates(event)
    event_id = event.get("guid")

    max_duration = get_app_config("MAX_MULTI_DAY_EVENT_DURATION") or 365
    if (dates["end"] - dates["start"]).days > max_duration:
        raise SuperdeskApiError.badRequestError(
            f"Failed to ingest Event with id '{event_id}': duration exceeds maximum allowed"
        )


def get_event_dates(event: dict[str, Any]):
    if not isinstance(event["dates"]["start"], datetime):
        event["dates"]["start"] = datetime.strptime(event["dates"]["start"], "%Y-%m-%dT%H:%M:%S+0000")
    if not isinstance(event["dates"]["end"], datetime):
        event["dates"]["end"] = datetime.strptime(event["dates"]["end"], "%Y-%m-%dT%H:%M:%S+0000")
    event["dates"].setdefault("all_day", False)
    event["dates"].setdefault("no_end_time", False)
    return event["dates"]


def fix_hrefs(doc: dict[str, Any]):
    if doc.get("renditions"):
        app = get_current_wsgi_app()
        for key, rendition in doc["renditions"].items():
            if rendition.get("media"):
                rendition["href"] = app.upload_url(rendition["media"])
    for assoc in doc.get("associations", {}).values():
        fix_hrefs(assoc)


async def test_signature(request: Request):
    """Test if request is signed using app PUSH_KEY."""
    key = get_app_config(KEY)
    if not key:
        if not get_app_config("TESTING"):
            logger.warning("PUSH_KEY is not configured, can not verify incoming data.")
        return True
    payload = await request.get_data()

    mac = hmac.new(key, payload, "sha1")
    return hmac.compare_digest(request.get_header("x-superdesk-signature") or "", "sha1=%s" % mac.hexdigest())


async def assert_test_signature(request: Request):
    if not await test_signature(request):
        flask_req = request.request
        logger.warning("signature invalid on push from %s", flask_req.referrer or flask_req.remote_addr)
        await request.abort(403)
