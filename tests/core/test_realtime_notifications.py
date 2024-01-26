from unittest import mock
from datetime import datetime

from flask import json
from superdesk import get_resource_service
from newsroom.push import notify_new_agenda_item
from newsroom.tests.users import ADMIN_USER_ID

from .test_push import get_signature_headers
from ..utils import mock_send_email


@mock.patch("newsroom.email.send_email", mock_send_email)
def test_realtime_notifications_wire(client, app, mocker):
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

    with app.mail.record_messages() as outbox:
        key = b"something random"
        app.config["PUSH_KEY"] = key
        data = json.dumps(
            {
                "guid": "topic1_item1",
                "type": "text",
                "slugline": "That's the test slugline cheese",
                "headline": "Demo Article",
                "body_html": "Story that involves cheese and onions",
            }
        )
        push_mock = mocker.patch("newsroom.notifications.push_notification")
        headers = get_signature_headers(data, key)
        resp = client.post("/push", data=data, content_type="application/json", headers=headers)
        assert 200 == resp.status_code

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
def test_agenda_notifications(app, mocker):
    user = app.data.find_one("users", req=None, _id=ADMIN_USER_ID)
    app.data.insert(
        "topics",
        [
            {
                "user": user["_id"],
                "label": "Cheesy Stuff",
                "query": "cheese",
                "topic_type": "agenda",
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
                "topic_type": "agenda",
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
        "agenda",
        [
            {
                "_id": "event_id",
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

    # avoid using client to mimic celery worker
    with app.mail.record_messages() as outbox:
        notify_new_agenda_item("event_id")

    notification = get_resource_service("notifications").find_one(req=None, user=user["_id"])
    assert notification is not None
    assert notification["action"] == "topic_matches"
    assert notification["item"] == "event_id"
    assert notification["resource"] == "agenda"
    assert notification["user"] == user["_id"]

    # Only 1 email should have been sent (not 3)
    assert len(outbox) == 1
    assert "http://localhost:5050/agenda?item=event_id" in outbox[0].body
