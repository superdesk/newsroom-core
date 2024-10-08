import logging
from typing import Any, Callable, Literal

from pydantic import BaseModel
from quart_babel import gettext

from superdesk.lock import lock, unlock
from superdesk import get_resource_service
from superdesk.core.web import EndpointGroup, Request, Response
from superdesk.core import json, get_app_config

from newsroom import signals
from newsroom.utils import parse_date_str
from newsroom.assets import ASSETS_RESOURCE
from newsroom.core import get_current_wsgi_app
from newsroom.flask import get_file_from_request
from newsroom.web.factory import NewsroomWebApp
from newsroom.wire.views import delete_dashboard_caches

from .publishing import Publisher
from .utils import assert_test_signature
from .tasks import notify_new_agenda_item, notify_new_wire_item
from .notifications import NotificationManager


logger = logging.getLogger(__name__)
push_endpoints = EndpointGroup("push", __name__)
notifier = NotificationManager()
publisher = Publisher()

PublishHandlerFunc = Callable[[NewsroomWebApp, dict[str, Any]], None]


def handle_publish_event(app: NewsroomWebApp, item):
    orig = app.data.find_one("agenda", req=None, _id=item["guid"])
    event_id = publisher.publish_event(item, orig)
    notify_new_agenda_item.delay(event_id, check_topics=True, is_new=orig is None)


def handle_publish_planning(app: NewsroomWebApp, item):
    orig = app.data.find_one("agenda", req=None, _id=item["guid"]) or {}
    item["planning_date"] = parse_date_str(item["planning_date"])

    plan_id = publisher.publish_planning_item(item, orig)
    event_id = publisher.publish_planning_into_event(item)

    # Prefer parent Event when sending notificaitons
    _id = event_id or plan_id
    notify_new_agenda_item.delay(_id, check_topics=True, is_new=orig is None)


def handle_publish_text_item(_, item):
    orig = get_resource_service("items").find_one(req=None, _id=item["guid"])
    item["_id"] = publisher.publish_item(item, orig)

    if not item.get("nextversion"):
        notify_new_wire_item.delay(
            item["_id"], check_topics=orig is None or get_app_config("WIRE_NOTIFICATIONS_ON_CORRECTIONS")
        )


def handle_publish_planning_featured(_, item):
    assert item.get("_id"), {"_id": 1}
    service = get_resource_service("agenda_featured")
    orig = service.find_one(req=None, _id=item["_id"])

    if orig:
        service.update(orig["_id"], {"items": item.get("items") or []}, orig)
    else:
        # Assert `tz` and `items` in initial push only
        assert item.get("tz"), {"tz": 1}
        assert item.get("items"), {"items": 1}
        service.create([item])


def get_publish_handler(
    item_type: Literal["event", "planning", "text", "planning_featured"]
) -> PublishHandlerFunc | None:
    handlers = {
        "event": handle_publish_event,
        "planning": handle_publish_planning,
        "text": handle_publish_text_item,
        "planning_featured": handle_publish_planning_featured,
    }

    return handlers.get(item_type)


class RouteArguments(BaseModel):
    media_id: str


@push_endpoints.endpoint("/push", methods=["POST"])
async def push(request: Request):
    await assert_test_signature(request)
    item = json.loads(await request.get_data())

    assert "guid" in item or "_id" in item, {"guid": 1}
    assert "type" in item, {"type": 1}

    lock_name = f"push-{item.get('guid') or item.get('_id')}"
    if not lock(lock_name, expire=60):
        await request.abort(503)

    try:
        app = get_current_wsgi_app()
        signals.push.send(app, item=item)

        item_type = item.get("type")
        publish_fn = get_publish_handler(item_type)

        if publish_fn:
            publish_fn(app, item)

        else:
            await request.abort(400, gettext("Unknown type {}".format(item.get("type"))))

        if get_app_config("DELETE_DASHBOARD_CACHE_ON_PUSH", True):
            delete_dashboard_caches()

        return Response({})

    finally:
        unlock(lock_name)


# keeping this for testing
@push_endpoints.endpoint("/notify", methods=["POST"])
async def notify(request: Request):
    data = json.loads(await request.get_data())
    await notifier.notify_new_item(data["item"])
    return Response({"status": "OK"})


@push_endpoints.endpoint("/push_binary", methods=["POST"])
async def push_binary(request: Request):
    await assert_test_signature(request)

    media = await get_file_from_request("media")
    if media is None:
        await request.abort(403)

    assert media is not None

    media_id = (await request.get_form())["media_id"]
    app = get_current_wsgi_app()
    await app.media_async.put(media, media_id, resource=ASSETS_RESOURCE, _id=media_id, content_type=media.content_type)
    return Response({"status": "OK"}, 201)


@push_endpoints.endpoint("/push_binary/<string:media_id>")
async def push_binary_get(args: RouteArguments, _: None, request: Request):
    app = get_current_wsgi_app()
    media_file = await app.media_async.get(args.media_id, resource=ASSETS_RESOURCE)
    if media_file:
        return Response({})

    await request.abort(404)
