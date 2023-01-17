from bson import ObjectId
from flask import json
from pytest import fixture
from copy import deepcopy
from newsroom.notifications import get_user_notifications
from tests.fixtures import (  # noqa: F401
    items,
    init_items,
    agenda_items,
    init_agenda_items,
    init_auth,
    PUBLIC_USER_ID,
    COMPANY_1_ID,
)
from tests.utils import post_json, mock_send_email
from .test_push_events import test_event, test_planning
from unittest import mock

NAV_1 = ObjectId("5e65964bf5db68883df561c0")
NAV_2 = ObjectId("5e65964bf5db68883df561c1")


@fixture(autouse=True)
def set_events_only_company(app):
    company = app.data.find_one("companies", None, _id=COMPANY_1_ID)
    assert company is not None
    updates = {
        "events_only": True,
        "section": {"wire": True, "agenda": True},
        "is_enabled": True,
    }
    app.data.update("companies", COMPANY_1_ID, updates, company)
    company = app.data.find_one("companies", None, _id=COMPANY_1_ID)
    assert company.get("events_only") is True
    user = app.data.find_one("users", None, _id=PUBLIC_USER_ID)
    assert user is not None
    app.data.update("users", PUBLIC_USER_ID, {"is_enabled": True, "receive_email": True}, user)


def set_products(app):
    app.data.insert(
        "navigations",
        [
            {
                "_id": NAV_1,
                "name": "navigation-1",
                "is_enabled": True,
                "product_type": "agenda",
            },
            {
                "_id": NAV_2,
                "name": "navigation-2",
                "is_enabled": True,
                "product_type": "agenda",
            },
        ],
    )

    app.data.insert(
        "products",
        [
            {
                "_id": 12,
                "name": "product test",
                "query": "headline:test",
                "companies": [COMPANY_1_ID],
                "navigations": [NAV_1],
                "is_enabled": True,
                "product_type": "agenda",
            },
            {
                "_id": 13,
                "name": "product test 2",
                "query": "slugline:prime",
                "companies": [COMPANY_1_ID],
                "navigations": [NAV_2],
                "is_enabled": True,
                "product_type": "agenda",
            },
        ],
    )


def test_item_json(client):
    # public user
    with client.session_transaction() as session:
        session["user"] = PUBLIC_USER_ID
        session["user_type"] = "public"

    resp = client.get("/agenda/urn:conference?format=json")
    data = json.loads(resp.get_data())
    assert "headline" in data
    assert "planning_items" not in data
    assert "coverages" not in data


def test_search(client, app):
    # public user
    set_products(app)
    with client.session_transaction() as session:
        session["user"] = PUBLIC_USER_ID
        session["user_type"] = "public"

    resp = client.get("/agenda/search")
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])
    assert "_aggregations" in data
    assert "urgency" not in data["_aggregations"]
    assert "coverage" not in data["_aggregations"]
    assert "planning_items" not in data["_aggregations"]
    assert "planning_items" not in data["_items"][0]
    assert "coverages" not in data["_items"][0]

    resp = client.get(f"/agenda/search?navigation={NAV_1}")
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])
    assert "_aggregations" in data
    assert "urgency" not in data["_aggregations"]
    assert "coverage" not in data["_aggregations"]
    assert "planning_items" not in data["_aggregations"]
    assert "planning_items" not in data["_items"][0]
    assert "coverages" not in data["_items"][0]


def set_watch_products(app):
    app.data.insert(
        "navigations",
        [
            {
                "_id": NAV_1,
                "name": "navigation-1",
                "is_enabled": True,
                "product_type": "agenda",
            }
        ],
    )

    app.data.insert(
        "products",
        [
            {
                "_id": 12,
                "name": "product test",
                "query": "press",
                "companies": [COMPANY_1_ID],
                "navigations": [NAV_1],
                "is_enabled": True,
                "product_type": "agenda",
            }
        ],
    )


@mock.patch("newsroom.email.send_email", mock_send_email)
def test_watched_event_sends_notification_for_event_update(client, app, mocker):
    event = deepcopy(test_event)
    post_json(client, "/push", event)
    set_watch_products(app)

    with client.session_transaction() as session:
        session["user"] = PUBLIC_USER_ID
        session["user_type"] = "public"

    post_json(client, "/agenda_watch", {"items": [event["guid"]]})

    # update comes in
    event["state"] = "rescheduled"
    event["dates"] = {
        "start": "2018-05-27T08:00:00+0000",
        "end": "2018-06-30T09:00:00+0000",
        "tz": "Australia/Sydney",
    }

    push_mock = mocker.patch("newsroom.notifications.push_notification")
    with app.mail.record_messages() as outbox:
        post_json(client, "/push", event)
    notifications = get_user_notifications(PUBLIC_USER_ID)

    assert len(outbox) == 1
    assert "Subject: Prime minister press conference - updated" in str(outbox[0])

    assert push_mock.call_args[0][0] == "new_notifications"
    assert str(PUBLIC_USER_ID) in push_mock.call_args[1]["counts"].keys()

    assert len(notifications) == 1
    assert notifications[0]["_id"] == "{}_foo".format(PUBLIC_USER_ID)
    assert notifications[0]["action"] == "watched_agenda_updated"
    assert notifications[0]["item"] == "foo"
    assert notifications[0]["resource"] == "agenda"
    assert notifications[0]["user"] == PUBLIC_USER_ID


# @mock.patch('newsroom.agenda.email.send_email', mock_send_email)
@mock.patch("newsroom.email.send_email", mock_send_email)
def test_watched_event_sends_notification_for_unpost_event(client, app, mocker):
    event = deepcopy(test_event)
    set_watch_products(app)
    post_json(client, "/push", event)

    with client.session_transaction() as session:
        session["user"] = PUBLIC_USER_ID
        session["user_type"] = "public"

    post_json(client, "/agenda_watch", {"items": [event["guid"]]})

    # update the event for unpost
    event["pubstatus"] = "cancelled"
    event["state"] = "cancelled"

    push_mock = mocker.patch("newsroom.notifications.push_notification")
    with app.mail.record_messages() as outbox:
        post_json(client, "/push", event)
    notifications = get_user_notifications(PUBLIC_USER_ID)

    assert len(outbox) == 1
    assert "Subject: Prime minister press conference - updated" in str(outbox[0])

    assert push_mock.call_args[0][0] == "new_notifications"
    assert str(PUBLIC_USER_ID) in push_mock.call_args[1]["counts"].keys()

    assert len(notifications) == 1
    assert notifications[0]["_id"] == "{}_foo".format(PUBLIC_USER_ID)
    assert notifications[0]["action"] == "watched_agenda_updated"
    assert notifications[0]["item"] == "foo"
    assert notifications[0]["resource"] == "agenda"
    assert notifications[0]["user"] == PUBLIC_USER_ID


@mock.patch("newsroom.email.send_email", mock_send_email)
def test_watched_event_sends_notification_for_added_planning(client, app, mocker):
    event = deepcopy(test_event)
    post_json(client, "/push", event)
    set_watch_products(app)

    with client.session_transaction() as session:
        session["user"] = PUBLIC_USER_ID
        session["user_type"] = "public"

    post_json(client, "/agenda_watch", {"items": [event["guid"]]})

    # planning comes in
    planning = deepcopy(test_planning)

    push_mock = mocker.patch("newsroom.notifications.push_notification")
    with app.mail.record_messages() as outbox:
        post_json(client, "/push", planning)
    notifications = get_user_notifications(PUBLIC_USER_ID)

    assert len(outbox) == 0
    assert len(notifications) == 0
    push_mock.assert_not_called()


@mock.patch("newsroom.email.send_email", mock_send_email)
def test_watched_event_sends_notification_for_cancelled_planning(client, app, mocker):
    event = deepcopy(test_event)
    planning = deepcopy(test_planning)
    set_watch_products(app)
    post_json(client, "/push", event)
    post_json(client, "/push", planning)

    with client.session_transaction() as session:
        session["user"] = PUBLIC_USER_ID
        session["user_type"] = "public"

    post_json(client, "/agenda_watch", {"items": [event["guid"]]})

    # update the planning for cancel
    planning["pubstatus"] = "cancelled"
    planning["state"] = "cancelled"

    push_mock = mocker.patch("newsroom.notifications.push_notification")
    with app.mail.record_messages() as outbox:
        post_json(client, "/push", planning)
    notifications = get_user_notifications(PUBLIC_USER_ID)

    assert len(outbox) == 0
    assert len(notifications) == 0
    push_mock.assert_not_called()


@mock.patch("newsroom.email.send_email", mock_send_email)
def test_watched_event_sends_notification_for_added_coverage(client, app, mocker):
    event = deepcopy(test_event)
    planning = deepcopy(test_planning)
    set_watch_products(app)
    post_json(client, "/push", event)
    post_json(client, "/push", planning)

    with client.session_transaction() as session:
        session["user"] = PUBLIC_USER_ID
        session["user_type"] = "public"

    post_json(client, "/agenda_watch", {"items": [event["guid"]]})

    # update the planning with an added coverage
    planning["coverages"].append(
        {
            "planning": {
                "g2_content_type": "video",
                "slugline": "Vivid planning item",
                "internal_note": "internal note here",
                "genre": [{"name": "Article (news)", "qcode": "Article"}],
                "ednote": "ed note here",
                "scheduled": "2018-05-29T10:51:52+0000",
            },
            "coverage_status": {
                "name": "coverage intended",
                "label": "Planned",
                "qcode": "ncostat:int",
            },
            "workflow_status": "draft",
            "firstcreated": "2018-05-29T10:55:00+0000",
            "coverage_id": "coverage-3",
        }
    )

    push_mock = mocker.patch("newsroom.notifications.push_notification")
    with app.mail.record_messages() as outbox:
        post_json(client, "/push", planning)
    notifications = get_user_notifications(PUBLIC_USER_ID)

    assert len(outbox) == 0
    assert len(notifications) == 0
    push_mock.assert_not_called()
