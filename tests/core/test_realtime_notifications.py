import quart

from unittest import mock
from datetime import datetime, timedelta

from bson import ObjectId
from newsroom.tests import markers
from superdesk import get_resource_service
from newsroom.push import notify_new_agenda_item, notify_new_wire_item
from newsroom.tests.fixtures import COMPANY_1_ID, PUBLIC_USER_ID
from newsroom.tests.users import ADMIN_USER_ID
from tests.core.utils import create_entries_for

from ..utils import mock_send_email


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_realtime_notifications_wire(app, mocker, company_products):
    user = app.data.find_one("users", req=None, _id=PUBLIC_USER_ID)
    navigations = [
        {
            "_id": ObjectId(),
            "name": "Food",
            "product_type": "wire",
            "is_enabled": True,
        },
        {
            "_id": ObjectId(),
            "name": "Sport",
            "product_type": "wire",
            "is_enabled": True,
        },
    ]

    await create_entries_for("navigations", navigations)

    for product in company_products:
        if "*" in product["query"]:
            # we want only products which will filter out everything
            continue
        updates = {"navigations": [navigations[0]["_id"]]}
        app.data.update("products", product["_id"], updates, product)

    await create_entries_for(
        "topics",
        [
            {
                "_id": ObjectId(),
                "user": user["_id"],
                "label": "Cheesy Stuff",
                "query": "cheese",
                "topic_type": "wire",
                "subscribers": [
                    {
                        "user_id": user["_id"],
                        "notification_type": "real-time",
                    },
                ],
            },
            {
                "_id": ObjectId(),
                "user": user["_id"],
                "label": "Onions",
                "query": "onions",
                "topic_type": "wire",
                "subscribers": [
                    {
                        "user_id": user["_id"],
                        "notification_type": "real-time",
                    },
                ],
            },
            {
                "_id": ObjectId(),
                "user": user["_id"],
                "label": "Company products",
                "query": "*:*",
                "topic_type": "wire",
                "subscribers": [
                    {
                        "user_id": user["_id"],
                        "notification_type": "real-time",
                    },
                ],
                "navigation": [navigations[0]["_id"]],
            },
        ],
    )

    app.data.insert(
        "items",
        [
            {
                "_id": "topic1_item1",
                "type": "text",
                "slugline": "That's the test slugline cheese",
                "headline": "Demo Article",
                "body_html": "Story that involves cheese and onions",
                "versioncreated": datetime.utcnow(),
            },
            {
                "_id": "item_other",
                "type": "text",
                "slugline": "other",
                "headline": "other",
                "body_html": "other",
                "versioncreated": datetime.utcnow(),
            },
        ],
    )

    push_mock = mocker.patch("newsroom.notifications.push_notification")
    with app.mail.record_messages() as outbox:
        assert not quart.request
        await notify_new_wire_item("topic1_item1")
        await notify_new_wire_item("item_other")

    assert push_mock.call_args[0][0] == "new_notifications"
    assert str(user["_id"]) in push_mock.call_args[1]["counts"].keys()

    notification = get_resource_service("notifications").find_one(req=None, user=user["_id"])
    assert notification["action"] == "topic_matches"
    assert notification["item"] == "topic1_item1"
    assert notification["resource"] == "wire"
    assert notification["user"] == user["_id"]

    # Only 1 email should have been sent (not 3)
    assert len(outbox) == 1
    assert "http://localhost:5050/wire?item=topic1_item1" in outbox[0].body

    # test notification after removing company products
    company = app.data.find_one("companies", req=None, _id=user["company"])
    app.data.update("companies", company["_id"], {"products": []}, company)

    with app.mail.record_messages() as outbox:
        await notify_new_wire_item("topic1_item1")

    assert len(outbox) == 0


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_realtime_notifications_agenda(app, mocker):
    await create_entries_for(
        "topics",
        [
            {
                "_id": ObjectId(),
                "user": ADMIN_USER_ID,
                "label": "Cheesy Stuff",
                "query": "cheese",
                "topic_type": "agenda",
                "subscribers": [
                    {
                        "user_id": ADMIN_USER_ID,
                        "notification_type": "real-time",
                    },
                ],
                "filter": {
                    "language": ["en"],
                },
            },
            {
                "_id": ObjectId(),
                "user": ADMIN_USER_ID,
                "label": "Onions",
                "query": "onions",
                "topic_type": "agenda",
                "subscribers": [
                    {
                        "user_id": ADMIN_USER_ID,
                        "notification_type": "real-time",
                    },
                ],
            },
            {
                "_id": ObjectId(),
                "user": PUBLIC_USER_ID,
                "label": "Test",
                "query": "cheese",
                "topic_type": "agenda",
                "subscribers": [
                    {
                        "user_id": PUBLIC_USER_ID,
                        "notification_type": "real-time",
                    },
                ],
            },
            {
                "_id": ObjectId(),
                "user": ADMIN_USER_ID,
                "label": "Should not match anything",
                "query": None,
                "topic_type": "agenda",
                "subscribers": [
                    {
                        "user_id": ADMIN_USER_ID,
                        "notification_type": "real-time",
                    },
                ],
                "filter": {
                    "language": ["foo"],
                },
            },
        ],
    )

    topic_id = ObjectId()

    app.data.insert(
        "products",
        [
            {
                "_id": topic_id,
                "name": "agenda product",
                "query": "*:*",
                "is_enabled": True,
                "product_type": "agenda",
            },
        ],
    )

    company = app.data.find_one("companies", req=None, _id=COMPANY_1_ID)
    assert company
    app.data.update(
        "companies", company["_id"], {"products": [{"_id": topic_id, "seats": 0, "section": "agenda"}]}, company
    )

    app.data.insert(
        "agenda",
        [
            {
                "_id": "event_id_1",
                "type": "agenda",
                "versioncreated": datetime.utcnow(),
                "name": "cheese event",
                "language": "en",
                "dates": {
                    "start": datetime.utcnow(),
                    "end": datetime.utcnow(),
                },
            },
            {
                "_id": "event_id_2",
                "type": "agenda",
                "versioncreated": datetime.utcnow(),
                "name": "another event",
                "language": "en",
                "dates": {
                    "start": datetime.utcnow(),
                    "end": datetime.utcnow(),
                },
            },
        ],
    )

    # avoid using client to mimic celery worker
    with app.mail.record_messages() as outbox:
        assert not quart.request
        await notify_new_agenda_item("event_id_1")
        await notify_new_agenda_item("event_id_2")

    notification = get_resource_service("notifications").find_one(req=None, user=ADMIN_USER_ID)
    assert notification is not None
    assert notification["action"] == "topic_matches"
    assert notification["item"] == "event_id_1"
    assert notification["resource"] == "agenda"
    assert str(notification["user"]) == ADMIN_USER_ID

    assert len(outbox) == 2
    assert "http://localhost:5050/agenda?item=event_id_1" in outbox[0].body


async def test_realtime_notifications_agenda_reccuring_event(app):
    app.data.insert(
        "agenda",
        [
            {
                "_id": "event_id_1",
                "type": "agenda",
                "versioncreated": datetime.utcnow(),
                "name": "cheese event",
                "dates": {
                    "start": datetime.utcnow(),
                    "end": datetime.utcnow(),
                },
                "recurrence_id": "event_id_1",
            },
            {
                "_id": "event_id_2",
                "type": "agenda",
                "versioncreated": datetime.utcnow(),
                "name": "another event",
                "dates": {
                    "start": datetime.utcnow(),
                    "end": datetime.utcnow(),
                },
                "recurrence_id": "event_id_1",
            },
        ],
    )

    with mock.patch("newsroom.push.notify_new_item") as notify_new_item:
        await notify_new_agenda_item("event_id_1")
        assert notify_new_item.call_count == 1

        await notify_new_agenda_item("event_id_2", is_new=True)
        assert notify_new_item.call_count == 1

        await notify_new_agenda_item("event_id_2")
        assert notify_new_item.call_count == 2


@markers.requires_async_celery
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_pause_notifications(app, mocker, company_products):
    user = app.data.find_one("users", req=None, _id=PUBLIC_USER_ID)
    updates = {
        "notification_schedule": dict(
            pause_from=(datetime.now() - timedelta(days=1)).date().isoformat(),
            pause_to=(datetime.now() + timedelta(days=1)).date().isoformat(),
        )
    }
    app.data.update("users", user["_id"], updates, user)

    app.data.insert(
        "agenda",
        [
            {
                "_id": "event_id_1",
                "type": "agenda",
                "versioncreated": datetime.utcnow(),
                "name": "cheese event",
                "dates": {
                    "start": datetime.utcnow(),
                    "end": datetime.utcnow(),
                },
            },
        ],
    )

    app.data.insert(
        "items",
        [
            {
                "_id": "item1",
                "type": "text",
                "slugline": "That's the test slugline cheese",
                "headline": "Demo Article",
                "body_html": "Story that involves cheese and onions",
            },
        ],
    )

    await create_entries_for(
        "topics",
        [
            {
                "_id": ObjectId(),
                "user": PUBLIC_USER_ID,
                "label": "All wire",
                "query": "*:*",
                "topic_type": "wire",
                "subscribers": [
                    {
                        "user_id": PUBLIC_USER_ID,
                        "notification_type": "real-time",
                    },
                ],
            },
            {
                "_id": ObjectId(),
                "user": PUBLIC_USER_ID,
                "label": "All agenda",
                "query": "*:*",
                "topic_type": "agenda",
                "subscribers": [
                    {
                        "user_id": PUBLIC_USER_ID,
                        "notification_type": "real-time",
                    },
                ],
            },
        ],
    )

    push_mock = mocker.patch("newsroom.notifications.push_notification")
    with app.mail.record_messages() as outbox:
        await notify_new_agenda_item("event_id_1")
        await notify_new_wire_item("item1")
        assert len(outbox) == 0
        push_mock.assert_not_called()
