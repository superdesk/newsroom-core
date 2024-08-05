import io
import os
import hmac
import bson
from flask import json
import pytest
from quart.datastructures import FileStorage
from datetime import datetime, timedelta
from superdesk import get_resource_service
from newsroom.tests.fixtures import TEST_USER_ID  # noqa - Fix cyclic import when running single test file
from newsroom.utils import get_company_dict, get_entity_or_404, get_user_dict
from tests.core.utils import add_company_products
from ..fixtures import COMPANY_1_ID, PUBLIC_USER_ID
from ..utils import mock_send_email
from unittest import mock


def get_signature_headers(data, key):
    mac = hmac.new(key, data.encode(), "sha1")
    return {"x-superdesk-signature": "sha1=%s" % mac.hexdigest()}


item = {
    "guid": "foo",
    "type": "text",
    "headline": "Foo",
    "firstcreated": "2017-11-27T08:00:57+0000",
    "body_html": "<p>foo bar</p>",
    "renditions": {
        "thumbnail": {
            "href": "http://example.com/foo",
            "media": "foo",
        }
    },
    "genre": [{"name": "News", "code": "news"}],
    "associations": {
        "featured": {
            "type": "picture",
            "renditions": {
                "thumbnail": {
                    "href": "http://example.com/bar",
                    "media": "bar",
                }
            },
        }
    },
    "event_id": "urn:event/1",
    "coverage_id": "urn:coverage/1",
    "subject": [
        {"name": "a", "code": "a", "scheme": "a"},
        {"name": "b", "code": "b", "scheme": "b"},
    ],
}


def test_push_item_inserts_missing(client, app):
    assert not app.config["PUSH_KEY"]
    resp = client.post("/push", data=json.dumps(item), content_type="application/json")
    assert 200 == resp.status_code

    resp = client.get("wire/foo?format=json")
    assert 200 == resp.status_code
    data = json.loads(resp.get_data())
    assert "/assets/foo" == data["renditions"]["thumbnail"]["href"]
    assert "/assets/bar" == data["associations"]["featured"]["renditions"]["thumbnail"]["href"]


def test_push_valid_signature(client, app, mocker):
    key = b"something random"
    app.config["PUSH_KEY"] = key
    data = json.dumps({"guid": "foo", "type": "text"})
    headers = get_signature_headers(data, key)
    resp = client.post("/push", data=data, content_type="application/json", headers=headers)
    assert 200 == resp.status_code


def test_notify_invalid_signature(client, app):
    app.config["PUSH_KEY"] = b"foo"
    data = json.dumps({})
    headers = get_signature_headers(data, b"bar")
    resp = client.post("/push", data=data, content_type="application/json", headers=headers)
    assert 403 == resp.status_code


async def test_push_binary(client_async):
    media_id = str(bson.ObjectId())

    resp = await client_async.get("/push_binary/%s" % media_id)
    assert 404 == resp.status_code

    resp = await client_async.post(
        "/push_binary",
        form={"media_id": media_id},
        files={"media": FileStorage(io.BytesIO(b"binary"), filename=media_id)},
    )
    assert 201 == resp.status_code

    resp = await client_async.get("/push_binary/%s" % media_id)
    assert 200 == resp.status_code

    with mock.patch("newsroom.assets.views.is_valid_session", return_value=True):
        resp = await client_async.get("/assets/%s" % media_id)
        assert 200 == resp.status_code


def get_fixture_path(fixture):
    return os.path.join(os.path.dirname(__file__), "..", "fixtures", fixture)


async def upload_binary(fixture, client_async, media_id=None):
    if not media_id:
        media_id = str(bson.ObjectId())

    with open(get_fixture_path(fixture), mode="rb") as pic:
        pic_content = pic.read()

        resp = await client_async.post(
            "/push_binary",
            form={"media_id": media_id},
            files={"media": FileStorage(io.BytesIO(pic_content), filename="picture.jpg")},
        )

        assert 201 == resp.status_code

    with mock.patch("newsroom.assets.views.is_valid_session", return_value=True):
        return await client_async.get("/assets/%s" % media_id)


async def test_push_binary_thumbnail_saves_copy(client_async):
    resp = await upload_binary("thumbnail.jpg", client_async)

    assert resp.content_type == "image/jpeg"

    with open(get_fixture_path("thumbnail.jpg"), mode="rb") as picture:
        assert resp.content_length == len(picture.read())


@pytest.mark.skip(reason="Fix once other views are moved to async")
def test_push_featuremedia_generates_renditions(client):
    media_id = str(bson.ObjectId())
    upload_binary("picture.jpg", client, media_id=media_id)
    item = {
        "guid": "test",
        "type": "text",
        "associations": {
            "featuremedia": {
                "type": "picture",
                "mimetype": "image/jpeg",
                "renditions": {
                    "4-3": {
                        "media": media_id,
                    },
                    "baseImage": {
                        "media": media_id,
                    },
                    "viewImage": {
                        "media": media_id,
                    },
                },
            }
        },
    }

    resp = client.post("/push", data=json.dumps(item), content_type="application/json")
    assert 200 == resp.status_code

    resp = client.get("/wire/test?format=json")
    data = json.loads(resp.get_data())
    assert 200 == resp.status_code
    picture = data["associations"]["featuremedia"]

    for name in ["thumbnail", "thumbnail_large", "view", "base"]:
        rendition = picture["renditions"]["_newsroom_%s" % name]
        resp = client.get(rendition["href"])
        assert 200 == resp.status_code


@pytest.mark.skip(reason="Fix once other views are moved to async")
async def test_push_update_removes_featuremedia(client):
    media_id = str(bson.ObjectId())
    upload_binary("picture.jpg", client, media_id=media_id)
    item = {
        "guid": "test",
        "type": "text",
        "version": 1,
        "associations": {
            "featuremedia": {
                "type": "picture",
                "mimetype": "image/jpeg",
                "renditions": {
                    "4-3": {
                        "media": media_id,
                    },
                    "baseImage": {
                        "media": media_id,
                    },
                    "viewImage": {
                        "media": media_id,
                    },
                },
            }
        },
    }

    resp = client.post("/push", data=json.dumps(item), content_type="application/json")
    assert 200 == resp.status_code

    resp = client.get("/wire/test?format=json")
    data = json.loads(resp.get_data())
    assert 200 == resp.status_code
    assert data["associations"] is not None

    item = {
        "guid": "test",
        "type": "text",
        "version": 2,
    }

    resp = client.post("/push", data=json.dumps(item), content_type="application/json")
    assert 200 == resp.status_code

    resp = client.get("/wire/test?format=json")
    data = json.loads(resp.get_data())
    assert 200 == resp.status_code
    assert data["associations"] is None


@pytest.mark.skip(reason="Fix once other views are moved to async")
def test_push_featuremedia_has_renditions_for_existing_media(client):
    media_id = str(bson.ObjectId())
    upload_binary("picture.jpg", client, media_id=media_id)
    item = {
        "guid": "test",
        "type": "text",
        "associations": {
            "featuremedia": {
                "type": "picture",
                "mimetype": "image/jpeg",
                "renditions": {
                    "4-3": {
                        "media": media_id,
                    },
                    "baseImage": {
                        "media": media_id,
                    },
                    "viewImage": {
                        "media": media_id,
                    },
                },
            }
        },
    }

    # First post
    resp = client.post("/push", data=json.dumps(item), content_type="application/json")
    assert 200 == resp.status_code

    # Second post
    resp = client.post("/push", data=json.dumps(item), content_type="application/json")
    assert 200 == resp.status_code

    resp = client.get("/wire/test?format=json")
    data = json.loads(resp.get_data())
    assert 200 == resp.status_code
    picture = data["associations"]["featuremedia"]

    for name in ["thumbnail", "thumbnail_large", "view", "base"]:
        rendition = picture["renditions"]["_newsroom_%s" % name]
        assert media_id in rendition["href"]
        resp = client.get(rendition["href"])
        assert 200 == resp.status_code


def test_push_binary_invalid_signature(client, app):
    app.config["PUSH_KEY"] = b"foo"
    resp = client.post(
        "/push_binary",
        data=dict(
            media_id=str(bson.ObjectId()),
            media=(io.BytesIO(b"foo"), "foo"),
        ),
    )
    assert 403 == resp.status_code


def test_notify_topic_matches_for_new_item(client, app, mocker):
    user_ids = app.data.insert(
        "users",
        [
            {
                "email": "foo2@bar.com",
                "first_name": "Foo",
                "is_enabled": True,
                "receive_email": True,
                "user_type": "administrator",
            }
        ],
    )

    with client as cli:
        with cli.session_transaction() as session:
            user = str(user_ids[0])
            session["user"] = user

        resp = cli.post(
            f"users/{user}/topics",
            json={
                "label": "bar",
                "query": "test",
                "subscribers": [{"user_id": user, "notification_type": "real-time"}],
                "is_global": False,
                "topic_type": "wire",
            },
        )
        assert 201 == resp.status_code

        resp = cli.post(
            f"users/{user}/topics",
            json={
                "label": "Sydney Weather",
                "subscribers": [{"user_id": user, "notification_type": "real-time"}],
                "is_global": False,
                "topic_type": "wire",
                "advanced": {
                    "all": "Weather Sydney",
                    "fields": ["headline", "body_html"],
                },
            },
        )
        assert 201 == resp.status_code

    key = b"something random"
    app.config["PUSH_KEY"] = key
    push_mock = mocker.patch("newsroom.push.push_notification")

    data = json.dumps({"guid": "foo", "type": "text", "headline": "this is a test"})
    headers = get_signature_headers(data, key)
    resp = client.post("/push", data=data, content_type="application/json", headers=headers)
    assert 200 == resp.status_code
    assert push_mock.call_args[1]["item"]["_id"] == "foo"
    assert len(push_mock.call_args[1]["topics"]) == 1

    data = json.dumps(
        {"guid": "syd_weather_1", "type": "text", "headline": "today", "body_html": "This is the weather for sydney"}
    )
    headers = get_signature_headers(data, key)
    resp = client.post("/push", data=data, content_type="application/json", headers=headers)
    assert 200 == resp.status_code
    assert push_mock.call_args[1]["item"]["_id"] == "syd_weather_1"
    assert len(push_mock.call_args[1]["topics"]) == 1


@mock.patch("newsroom.email.send_email", mock_send_email)
def test_notify_user_matches_for_new_item_in_history(client, app, mocker):
    company_ids = app.data.insert(
        "companies",
        [
            {
                "name": "Press 2 co.",
                "is_enabled": True,
            }
        ],
    )

    user = {
        "email": "foo2@bar.com",
        "first_name": "Foo",
        "is_enabled": True,
        "receive_email": True,
        "receive_app_notifications": True,
        "company": company_ids[0],
    }

    user_ids = app.data.insert("users", [user])
    user["_id"] = user_ids[0]

    app.data.insert(
        "history",
        docs=[
            {
                "version": "1",
                "_id": "bar",
            }
        ],
        action="download",
        user=user,
        section="wire",
    )

    with app.mail.record_messages() as outbox:
        key = b"something random"
        app.config["PUSH_KEY"] = key
        data = json.dumps({"guid": "bar", "type": "text", "headline": "this is a test"})
        push_mock = mocker.patch("newsroom.notifications.push_notification")
        headers = get_signature_headers(data, key)
        resp = client.post("/push", data=data, content_type="application/json", headers=headers)
        assert 200 == resp.status_code

        assert push_mock.call_args[0][0] == "new_notifications"
        assert str(user_ids[0]) in push_mock.call_args[1]["counts"].keys()

        notification = get_resource_service("notifications").find_one(req=None, user=user_ids[0])
        assert notification["action"] == "history_match"
        assert notification["item"] == "bar"
        assert notification["resource"] == "text"
        assert notification["user"] == user_ids[0]

        assert len(outbox) == 1
        assert "http://localhost:5050/wire?item=bar" in outbox[0].body

        outbox.clear()
        app.config["PUSH_KEY"] = None
        item = {"guid": "bar", "type": "text", "headline": "this is a test"}

        app.config["NOTIFY_MATCHING_USERS"] = "never"
        resp = client.post("/push", json=item)
        assert 200 == resp.status_code
        assert len(outbox) == 0

        item["pubstatus"] = "canceled"
        resp = client.post("/push", json=item)
        assert 200 == resp.status_code
        assert len(outbox) == 0

        app.config["NOTIFY_MATCHING_USERS"] = "cancel"
        resp = client.post("/push", json=item)
        assert 200 == resp.status_code
        assert len(outbox) == 1

        item["pubstatus"] = "usable"
        resp = client.post("/push", json=item)
        assert 200 == resp.status_code
        assert len(outbox) == 1


@mock.patch("newsroom.email.send_email", mock_send_email)
def test_notify_user_matches_for_killed_item_in_history(client, app, mocker):
    company_ids = app.data.insert(
        "companies",
        [
            {
                "name": "Press 2 co.",
                "is_enabled": True,
            }
        ],
    )

    user = {
        "email": "foo2@bar.com",
        "first_name": "Foo",
        "is_enabled": True,
        "receive_email": False,  # should still get email
        "receive_app_notifications": True,
        "company": company_ids[0],
    }

    user_ids = app.data.insert("users", [user])
    user["_id"] = user_ids[0]

    app.data.insert(
        "history",
        docs=[
            {
                "version": "1",
                "_id": "bar",
            }
        ],
        action="download",
        user=user,
    )

    key = b"something random"
    app.config["PUSH_KEY"] = key
    data = json.dumps(
        {
            "guid": "bar",
            "type": "text",
            "headline": "Kill Notice",
            "slugline": "Court",
            "description_html": "This story is killed",
            "body_html": "Killed story",
            "pubstatus": "canceled",
        }
    )
    push_mock = mocker.patch("newsroom.notifications.push_notification")
    headers = get_signature_headers(data, key)

    with app.mail.record_messages() as outbox:
        resp = client.post("/push", data=data, content_type="application/json", headers=headers)
        assert 200 == resp.status_code
        assert push_mock.call_args[0][0] == "new_notifications"
        assert str(user_ids[0]) in push_mock.call_args[1]["counts"].keys()
    assert len(outbox) == 1
    notification = get_resource_service("notifications").find_one(req=None, user=user_ids[0])
    assert notification["action"] == "history_match"
    assert notification["item"] == "bar"
    assert notification["resource"] == "text"
    assert notification["user"] == user_ids[0]


@mock.patch("newsroom.email.send_email", mock_send_email)
def test_notify_user_matches_for_new_item_in_bookmarks(client, app, mocker):
    user = {
        "email": "foo2@bar.com",
        "first_name": "Foo",
        "is_enabled": True,
        "is_approved": True,
        "receive_email": True,
        "receive_app_notifications": True,
        "company": COMPANY_1_ID,
    }

    user_ids = app.data.insert("users", [user])
    user["_id"] = user_ids[0]

    add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "name": "Service A",
                "query": "service.code: a",
                "is_enabled": True,
                "description": "Service A",
                "sd_product_id": None,
                "product_type": "wire",
            }
        ],
    )

    app.data.insert(
        "items",
        [
            {
                "_id": "bar",
                "headline": "testing",
                "service": [{"code": "a", "name": "Service A"}],
                "products": [{"code": 1, "name": "product-1"}],
            }
        ],
    )

    with client.session_transaction() as session:
        session["user"] = user["_id"]
        session["user_type"] = "public"
        session["name"] = "public"

    resp = client.post(
        "/wire_bookmark",
        data=json.dumps(
            {
                "items": ["bar"],
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 200

    with app.mail.record_messages() as outbox:
        key = b"something random"
        app.config["PUSH_KEY"] = key
        data = json.dumps({"guid": "bar", "type": "text", "headline": "this is a test"})
        push_mock = mocker.patch("newsroom.notifications.push_notification")
        headers = get_signature_headers(data, key)
        resp = client.post("/push", data=data, content_type="application/json", headers=headers)
        assert 200 == resp.status_code

        assert push_mock.call_args[0][0] == "new_notifications"
        assert str(user_ids[0]) in push_mock.call_args[1]["counts"].keys()

        notification = get_resource_service("notifications").find_one(req=None, user=user_ids[0])
        assert notification["action"] == "history_match"
        assert notification["item"] == "bar"
        assert notification["resource"] == "text"
        assert notification["user"] == user_ids[0]

    assert len(outbox) == 1
    assert "http://localhost:5050/wire?item=bar" in outbox[0].body


def test_do_not_notify_disabled_user(client, app, mocker):
    app.data.insert(
        "companies",
        [
            {
                "_id": 1,
                "name": "Press 2 co.",
                "is_enabled": True,
            }
        ],
    )

    user_ids = app.data.insert(
        "users",
        [
            {
                "email": "foo2@bar.com",
                "first_name": "Foo",
                "is_enabled": True,
                "receive_email": True,
                "company": 1,
            }
        ],
    )

    with client as cli:
        with cli.session_transaction() as session:
            user = str(user_ids[0])
            session["user"] = user
        resp = cli.post(
            "users/%s/topics" % user,
            json={"label": "bar", "query": "test", "notifications": True},
        )
        assert 201 == resp.status_code

    # disable user
    user = app.data.find_one("users", req=None, _id=user_ids[0])
    app.data.update("users", user_ids[0], {"is_enabled": False}, user)
    # clean cache
    app.cache.delete(str(user_ids[0]))

    key = b"something random"
    app.config["PUSH_KEY"] = key
    data = json.dumps({"guid": "foo", "type": "text", "headline": "this is a test"})
    push_mock = mocker.patch("newsroom.push.push_notification")
    headers = get_signature_headers(data, key)
    resp = client.post("/push", data=data, content_type="application/json", headers=headers)
    assert 200 == resp.status_code
    assert push_mock.call_args[1]["_items"][0]["_id"] == "foo"


@mock.patch("newsroom.email.send_email", mock_send_email)
def test_notify_checks_service_subscriptions(client, app, mocker):
    app.data.insert(
        "companies",
        [
            {
                "_id": 1,
                "name": "Press 2 co.",
                "is_enabled": True,
            }
        ],
    )

    user_ids = app.data.insert(
        "users",
        [
            {
                "email": "foo2@bar.com",
                "first_name": "Foo",
                "is_enabled": True,
                "receive_email": True,
                "company": 1,
            }
        ],
    )

    app.data.insert(
        "topics",
        [
            {
                "label": "topic-1",
                "query": "test",
                "user": user_ids[0],
                "notifications": True,
            },
            {
                "label": "topic-2",
                "query": "mock",
                "user": user_ids[0],
                "notifications": True,
            },
        ],
    )

    with client.session_transaction() as session:
        user = str(user_ids[0])
        session["user"] = user

    with app.mail.record_messages() as outbox:
        key = b"something random"
        app.config["PUSH_KEY"] = key
        data = json.dumps(
            {
                "guid": "foo",
                "type": "text",
                "headline": "this is a test",
                "service": [{"name": "Australian Weather", "code": "b"}],
            }
        )
        headers = get_signature_headers(data, key)
        resp = client.post("/push", data=data, content_type="application/json", headers=headers)
        assert 200 == resp.status_code
    assert len(outbox) == 0


@mock.patch("newsroom.email.send_email", mock_send_email)
def test_send_notification_emails(client, app):
    user_ids = app.data.insert(
        "users",
        [
            {
                "email": "foo2@bar.com",
                "first_name": "Foo",
                "is_enabled": True,
                "receive_email": True,
                "user_type": "administrator",
            }
        ],
    )

    app.data.insert(
        "topics",
        [
            {
                "label": "topic-1",
                "query": "test",
                "user": user_ids[0],
                "subscribers": [{"user_id": user_ids[0], "notification_type": "real-time"}],
                "is_global": False,
                "topic_type": "wire",
            },
            {
                "label": "topic-2",
                "query": "mock",
                "user": user_ids[0],
                "subscribers": [{"user_id": user_ids[0], "notification_type": "real-time"}],
                "is_global": False,
                "topic_type": "wire",
            },
        ],
    )

    with client.session_transaction() as session:
        user = str(user_ids[0])
        session["user"] = user

    with app.mail.record_messages() as outbox:
        key = b"something random"
        app.config["PUSH_KEY"] = key
        data = json.dumps(
            {
                "guid": "foo",
                "type": "text",
                "headline": "this is a test headline",
                "byline": "John Smith",
                "slugline": "This is the main slugline",
                "description_text": "This is the main description text",
            }
        )
        headers = get_signature_headers(data, key)
        resp = client.post("/push", data=data, content_type="application/json", headers=headers)
        assert 200 == resp.status_code
    assert len(outbox) == 1
    assert "http://localhost:5050/wire?item=foo" in outbox[0].body


def test_matching_topics(client, app):
    app.config["WIRE_AGGS"]["genre"] = {"terms": {"field": "genre.name", "size": 50}}
    client.post("/push", data=json.dumps(item), content_type="application/json")
    search = get_resource_service("wire_search")

    users = {"foo": {"company": "1", "user_type": "administrator", "_id": "foo"}}
    companies = {"1": {"_id": 1, "name": "test-comp"}}
    topics = [
        {"_id": "created_to_old", "created": {"to": "2017-01-01"}, "user": "foo"},
        {
            "_id": "created_from_future",
            "created": {"from": "now/d"},
            "user": "foo",
            "timezone_offset": 60 * 28,
        },
        {"_id": "filter", "filter": {"genre": ["other"]}, "user": "foo"},
        {"_id": "query", "query": "Foo", "user": "foo"},
    ]
    matching = search.get_matching_topics(item["guid"], topics, users, companies)
    assert ["created_from_future", "query"] == matching


def test_matching_topics_for_public_user(client, app):
    app.config["WIRE_AGGS"]["genre"] = {"terms": {"field": "genre.name", "size": 50}}
    add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "name": "Sport",
                "description": "Top level sport product",
                "sd_product_id": "p-1",
                "is_enabled": True,
                "product_type": "wire",
            }
        ],
    )

    item["products"] = [{"code": "p-1"}]
    client.post("/push", json=item)
    search = get_resource_service("wire_search")

    users = get_user_dict(use_globals=False)
    assert str(PUBLIC_USER_ID) in users
    companies = get_company_dict(use_globals=False)
    topics = [
        {"_id": "created_to_old", "created": {"to": "2017-01-01"}, "user": PUBLIC_USER_ID},
        {
            "_id": "created_from_future",
            "created": {"from": "now/d"},
            "user": PUBLIC_USER_ID,
            "timezone_offset": 60 * 28,
        },
        {"_id": "filter", "filter": {"genre": ["other"]}, "user": PUBLIC_USER_ID},
        {"_id": "query", "query": "Foo", "user": PUBLIC_USER_ID},
    ]
    matching = search.get_matching_topics(item["guid"], topics, users, companies)
    assert ["created_from_future", "query"] == matching


def test_matching_topics_for_user_with_inactive_company(client, app):
    app.config["WIRE_AGGS"]["genre"] = {"terms": {"field": "genre.name", "size": 50}}
    add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "name": "Sport",
                "description": "Top level sport product",
                "sd_product_id": "p-1",
                "is_enabled": True,
                "product_type": "wire",
            }
        ],
    )

    item["products"] = [{"code": "p-1"}]
    client.post("/push", json=item)
    search = get_resource_service("wire_search")

    users = get_user_dict(use_globals=False)
    companies = get_company_dict(use_globals=False)
    topics = [
        {"_id": "created_to_old", "created": {"to": "2017-01-01"}, "user": "bar"},
        {
            "_id": "created_from_future",
            "created": {"from": "now/d"},
            "user": PUBLIC_USER_ID,
            "timezone_offset": 60 * 28,
        },
        {"_id": "filter", "filter": {"genre": ["other"]}, "user": "bar"},
        {"_id": "query", "query": "Foo", "user": PUBLIC_USER_ID},
    ]
    with app.test_request_context():
        matching = search.get_matching_topics(item["guid"], topics, users, companies)
        assert ["created_from_future", "query"] == matching


def test_push_parsed_item(client, app):
    client.post("/push", data=json.dumps(item), content_type="application/json")
    parsed = get_entity_or_404(item["guid"], "wire_search")
    assert isinstance(parsed["firstcreated"], datetime)
    assert 2 == parsed["wordcount"]
    assert 7 == parsed["charcount"]


def test_push_parsed_dates(client, app):
    payload = item.copy()
    payload["embargoed"] = "2019-01-31T00:01:00+00:00"
    client.post("/push", data=json.dumps(payload), content_type="application/json")
    parsed = get_entity_or_404(item["guid"], "items")
    assert isinstance(parsed["firstcreated"], datetime)
    assert isinstance(parsed["versioncreated"], datetime)
    assert isinstance(parsed["embargoed"], datetime)


def test_push_event_coverage_info(client, app):
    client.post("/push", data=json.dumps(item), content_type="application/json")
    parsed = get_entity_or_404(item["guid"], "items")
    assert parsed["event_id"] == "urn:event/1"
    assert parsed["coverage_id"] == "urn:coverage/1"


def test_push_wire_subject_whitelist(client, app):
    app.config["WIRE_SUBJECT_SCHEME_WHITELIST"] = ["b"]
    client.post("/push", data=json.dumps(item), content_type="application/json")
    parsed = get_entity_or_404(item["guid"], "items")
    assert 1 == len(parsed["subject"])
    assert "b" == parsed["subject"][0]["name"]


def test_push_custom_expiry(client, app):
    app.config["SOURCE_EXPIRY_DAYS"] = {"foo": 50}
    updated = item.copy()
    updated["source"] = "foo"
    client.post("/push", data=json.dumps(updated), content_type="application/json")
    parsed = get_entity_or_404(item["guid"], "items")
    now = datetime.utcnow().replace(second=0, microsecond=0)
    expiry: datetime = parsed["expiry"].replace(tzinfo=None)
    assert now + timedelta(days=49) < expiry < now + timedelta(days=51)


def test_matching_topics_with_mallformed_query(client, app):
    add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "name": "Sport",
                "description": "Top level sport product",
                "sd_product_id": "p-1",
                "is_enabled": True,
                "product_type": "wire",
            }
        ],
    )

    item["products"] = [{"code": "p-1"}]
    client.post("/push", json=item)
    search = get_resource_service("wire_search")

    users = get_user_dict(use_globals=False)
    companies = get_company_dict(use_globals=False)
    topics = [
        {"_id": "good", "query": "*:*", "user": TEST_USER_ID},
        {"_id": "bad", "query": "AND Foo", "user": PUBLIC_USER_ID},
    ]
    with app.test_request_context():
        matching = search.get_matching_topics(item["guid"], topics, users, companies)
        assert ["good"] == matching


def test_matching_topics_when_disabling_section(client, app):
    add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "name": "All",
                "query": "*:*",
                "is_enabled": True,
                "product_type": "wire",
            }
        ],
    )

    client.post("/push", json=item)
    search = get_resource_service("wire_search")

    users = get_user_dict(use_globals=False)
    companies = get_company_dict(use_globals=False)
    topics = [
        {"_id": "all wire", "query": "*:*", "user": TEST_USER_ID, "topic_type": "wire"},
        {"_id": "all agenda", "query": "*:*", "user": TEST_USER_ID, "topic_type": "agenda"},
    ]
    users[str(TEST_USER_ID)]["sections"] = {"wire": False, "agenda": True}
    with app.test_request_context():
        matching = search.get_matching_topics(item["guid"], topics, users, companies)
        assert [] == matching
