import flask

from unittest import mock
from datetime import datetime

from bson import ObjectId
from superdesk import get_resource_service
from newsroom.push import notify_new_agenda_item, notify_new_wire_item
from newsroom.tests.fixtures import COMPANY_1_ID, PUBLIC_USER_ID
from newsroom.tests.users import ADMIN_USER_ID

from ..utils import mock_send_email


@mock.patch("newsroom.email.send_email", mock_send_email)
def test_realtime_notifications_wire(app, mocker):
    user = app.data.find_one("users", req=None, _id=ADMIN_USER_ID)
    app.data.insert(
        "topics",
        [
            {
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
        ],
    )
    app.data.insert(
        "history",
        docs=[{"version": "1", "_id": "topic1_item1"}],
        action="download",
        user=user,
        section="wire",
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
            },
            {
                "_id": "item_other",
                "type": "text",
                "slugline": "other",
                "headline": "other",
                "body_html": "other",
            },
        ],
    )

    push_mock = mocker.patch("newsroom.notifications.push_notification")
    with app.mail.record_messages() as outbox:
        assert not flask.request
        notify_new_wire_item("topic1_item1")
        notify_new_wire_item("item_other")

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


@mock.patch("newsroom.email.send_email", mock_send_email)
def test_realtime_notifications_agenda(app, mocker):
    app.data.insert(
        "topics",
        [
            {
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
                    "language": ["abcd"],  # filters are not applied atm, but can ruin the query
                },
            },
            {
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
                "dates": {
                    "start": datetime.utcnow(),
                    "end": datetime.utcnow(),
                },
            },
        ],
    )

    # avoid using client to mimic celery worker
    with app.mail.record_messages() as outbox:
        assert not flask.request
        notify_new_agenda_item("event_id_1")
        notify_new_agenda_item("event_id_2")

    notification = get_resource_service("notifications").find_one(req=None, user=ADMIN_USER_ID)
    assert notification is not None
    assert notification["action"] == "topic_matches"
    assert notification["item"] == "event_id_1"
    assert notification["resource"] == "agenda"
    assert str(notification["user"]) == ADMIN_USER_ID

    # Only 1 email should have been sent (not 3)
    assert len(outbox) == 2
    assert "http://localhost:5050/agenda?item=event_id_1" in outbox[0].body
