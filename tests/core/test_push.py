import io
import os
import hmac
import bson
from unittest import mock
from datetime import datetime, timedelta

from bson import ObjectId
from quart import json
from quart.datastructures import FileStorage

from superdesk import get_resource_service

from newsroom.types import UserResourceModel, CompanyResource, UserRole
from newsroom.utils import get_company_dict, get_entity_or_404, get_user_dict

from newsroom.tests.fixtures import TEST_USER_ID  # noqa - Fix cyclic import when running single test file
from newsroom.tests import markers
from tests.core.utils import add_company_products, create_entries_for
from ..fixtures import COMPANY_1_ID, PUBLIC_USER_ID
from ..utils import mock_send_email


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


async def test_push_item_inserts_missing(client, app):
    assert not app.config["PUSH_KEY"]
    resp = await client.post("/push", json=item)
    assert 200 == resp.status_code

    resp = await client.get("wire/foo?format=json")
    assert 200 == resp.status_code
    data = json.loads(await resp.get_data())
    assert "/assets/foo" == data["renditions"]["thumbnail"]["href"]
    assert "/assets/bar" == data["associations"]["featured"]["renditions"]["thumbnail"]["href"]


async def test_push_valid_signature(client, app, mocker):
    key = b"something random"
    app.config["PUSH_KEY"] = key
    data = {"guid": "foo", "type": "text"}
    headers = get_signature_headers(json.dumps(data), key)
    resp = await client.post("/push", json=data, headers=headers)
    assert 200 == resp.status_code


async def test_notify_invalid_signature(client, app):
    app.config["PUSH_KEY"] = b"foo"
    data = json.dumps({})
    headers = get_signature_headers(data, b"bar")
    resp = await client.post("/push", json={}, headers=headers)
    assert 403 == resp.status_code


async def test_push_binary(client):
    media_id = str(bson.ObjectId())

    resp = await client.get("/push_binary/%s" % media_id)
    assert 404 == resp.status_code

    resp = await client.post(
        "/push_binary",
        form=dict(media_id=media_id),
        files={"media": FileStorage(io.BytesIO(b"binary"), filename=media_id)},
    )
    assert 201 == resp.status_code

    resp = await client.get("/push_binary/%s" % media_id)
    assert 200 == resp.status_code

    resp = await client.get("/assets/%s" % media_id)
    assert 200 == resp.status_code


def get_fixture_path(fixture):
    return os.path.join(os.path.dirname(__file__), "..", "fixtures", fixture)


async def upload_binary(fixture, client, media_id=None):
    if not media_id:
        media_id = str(bson.ObjectId())
    with open(get_fixture_path(fixture), mode="rb") as pic:
        resp = await client.post(
            "/push_binary", form=dict(media_id=media_id), files=dict(media=FileStorage(pic, filename="picture.jpg"))
        )

        assert 201 == resp.status_code, await resp.get_data(as_text=True)
    return await client.get("/assets/%s" % media_id)


async def test_push_binary_thumbnail_saves_copy(client):
    resp = await upload_binary("thumbnail.jpg", client)
    assert resp.content_type == "image/jpeg"
    with open(get_fixture_path("thumbnail.jpg"), mode="rb") as picture:
        assert resp.content_length == len(picture.read())


async def test_push_featuremedia_generates_renditions(client):
    media_id = str(bson.ObjectId())
    await upload_binary("picture.jpg", client, media_id=media_id)
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

    resp = await client.post("/push", json=item)
    assert 200 == resp.status_code

    resp = await client.get("/wire/test?format=json")
    data = json.loads(await resp.get_data())
    assert 200 == resp.status_code
    picture = data["associations"]["featuremedia"]

    for name in ["thumbnail", "thumbnail_large", "view", "base"]:
        rendition = picture["renditions"]["_newsroom_%s" % name]
        resp = await client.get(rendition["href"])
        assert 200 == resp.status_code


async def test_push_update_removes_featuremedia(client):
    media_id = str(bson.ObjectId())
    await upload_binary("picture.jpg", client, media_id=media_id)
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

    resp = await client.post("/push", json=item)
    assert 200 == resp.status_code

    resp = await client.get("/wire/test?format=json")
    data = json.loads(await resp.get_data())
    assert 200 == resp.status_code
    assert data["associations"] is not None

    item = {
        "guid": "test",
        "type": "text",
        "version": 2,
    }

    resp = await client.post("/push", json=item)
    assert 200 == resp.status_code

    resp = await client.get("/wire/test?format=json")
    data = json.loads(await resp.get_data())
    assert 200 == resp.status_code
    assert data["associations"] is None


async def test_push_featuremedia_has_renditions_for_existing_media(client):
    media_id = str(bson.ObjectId())
    await upload_binary("picture.jpg", client, media_id=media_id)
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
    resp = await client.post("/push", json=item)
    assert 200 == resp.status_code

    # Second post
    resp = await client.post("/push", json=item)
    assert 200 == resp.status_code

    resp = await client.get("/wire/test?format=json")
    data = json.loads(await resp.get_data())
    assert 200 == resp.status_code
    picture = data["associations"]["featuremedia"]

    for name in ["thumbnail", "thumbnail_large", "view", "base"]:
        rendition = picture["renditions"]["_newsroom_%s" % name]
        assert media_id in rendition["href"]
        resp = await client.get(rendition["href"])
        assert 200 == resp.status_code


async def test_push_binary_invalid_signature(client, app):
    app.config["PUSH_KEY"] = b"foo"
    resp = await client.post(
        "/push_binary",
        form=dict(media_id=str(bson.ObjectId())),
        files={"media": FileStorage(io.BytesIO(b"foo"), filename="foo")},
    )
    assert 403 == resp.status_code


@markers.requires_async_celery
async def test_notify_topic_matches_for_new_item(client, app, mocker):
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

    async with client.session_transaction() as session:
        user = str(user_ids[0])
        session["user"] = user

    resp = await client.post(
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

    resp = await client.post(
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

    data = {"guid": "foo", "type": "text", "headline": "this is a test"}
    headers = get_signature_headers(json.dumps(data), key)
    resp = await client.post("/push", json=data, headers=headers)
    assert 200 == resp.status_code

    # TODO-ASYNC: TypeError: 'NoneType' object is not subscriptable
    assert push_mock.call_args[1]["item"]["_id"] == "foo"
    assert len(push_mock.call_args[1]["topics"]) == 1

    data = {"guid": "syd_weather_1", "type": "text", "headline": "today", "body_html": "This is the weather for sydney"}
    headers = get_signature_headers(json.dumps(data), key)
    resp = await client.post("/push", json=data, headers=headers)
    assert 200 == resp.status_code
    assert push_mock.call_args[1]["item"]["_id"] == "syd_weather_1"
    assert len(push_mock.call_args[1]["topics"]) == 1


@markers.requires_async_celery
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_notify_user_matches_for_new_item_in_history(client, app, mocker):
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
        data = {"guid": "bar", "type": "text", "headline": "this is a test"}
        push_mock = mocker.patch("newsroom.notifications.push_notification")
        headers = get_signature_headers(json.dumps(data), key)
        resp = await client.post("/push", json=data, headers=headers)
        assert 200 == resp.status_code

        # TODO-ASYNC: TypeError: 'NoneType' object is not subscriptable
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
        resp = await client.post("/push", json=item)
        assert 200 == resp.status_code
        assert len(outbox) == 0

        item["pubstatus"] = "canceled"
        resp = await client.post("/push", json=item)
        assert 200 == resp.status_code
        assert len(outbox) == 0

        app.config["NOTIFY_MATCHING_USERS"] = "cancel"
        resp = await client.post("/push", json=item)
        assert 200 == resp.status_code
        assert len(outbox) == 1

        item["pubstatus"] = "usable"
        resp = await client.post("/push", json=item)
        assert 200 == resp.status_code
        assert len(outbox) == 1


@markers.requires_async_celery
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_notify_user_matches_for_killed_item_in_history(client, app, mocker):
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
    data = {
        "guid": "bar",
        "type": "text",
        "headline": "Kill Notice",
        "slugline": "Court",
        "description_html": "This story is killed",
        "body_html": "Killed story",
        "pubstatus": "canceled",
    }
    push_mock = mocker.patch("newsroom.notifications.push_notification")
    headers = get_signature_headers(json.dumps(data), key)

    with app.mail.record_messages() as outbox:
        resp = await client.post("/push", json=data, headers=headers)
        assert 200 == resp.status_code

        # TODO-ASYNC: TypeError: 'NoneType' object is not subscriptable
        assert push_mock.call_args[0][0] == "new_notifications"
        assert str(user_ids[0]) in push_mock.call_args[1]["counts"].keys()
    assert len(outbox) == 1
    notification = get_resource_service("notifications").find_one(req=None, user=user_ids[0])
    assert notification["action"] == "history_match"
    assert notification["item"] == "bar"
    assert notification["resource"] == "text"
    assert notification["user"] == user_ids[0]


@markers.requires_async_celery
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_notify_user_matches_for_new_item_in_bookmarks(client, app, mocker):
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

    async with client.session_transaction() as session:
        session["user"] = str(user["_id"])
        session["user_type"] = "public"
        session["name"] = "public"

    resp = await client.post(
        "/wire_bookmark",
        json={"items": ["bar"]},
    )
    assert resp.status_code == 200

    with app.mail.record_messages() as outbox:
        key = b"something random"
        app.config["PUSH_KEY"] = key
        data = {"guid": "bar", "type": "text", "headline": "this is a test"}
        push_mock = mocker.patch("newsroom.notifications.push_notification")
        headers = get_signature_headers(json.dumps(data), key)
        resp = await client.post("/push", json=data, headers=headers)
        assert 200 == resp.status_code

        # TODO-ASYNC: TypeError: 'NoneType' object is not subscriptable
        assert push_mock.call_args[0][0] == "new_notifications"
        assert str(user_ids[0]) in push_mock.call_args[1]["counts"].keys()

        notification = get_resource_service("notifications").find_one(req=None, user=user_ids[0])
        assert notification["action"] == "history_match"
        assert notification["item"] == "bar"
        assert notification["resource"] == "text"
        assert notification["user"] == user_ids[0]

    assert len(outbox) == 1
    assert "http://localhost:5050/wire?item=bar" in outbox[0].body


@markers.requires_async_celery
async def test_do_not_notify_disabled_user(client, app, mocker):
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

    async with client.session_transaction() as session:
        user = str(user_ids[0])
        session["user"] = user
    resp = await client.post(
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
    data = {"guid": "foo", "type": "text", "headline": "this is a test"}
    push_mock = mocker.patch("newsroom.push.push_notification")
    headers = get_signature_headers(json.dumps(data), key)
    resp = await client.post("/push", json=data, headers=headers)
    assert 200 == resp.status_code
    # TODO-ASYNC: TypeError: 'NoneType' object is not subscriptable
    assert push_mock.call_args[1]["_items"][0]["_id"] == "foo"


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_notify_checks_service_subscriptions(client, app, mocker):
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

    await create_entries_for(
        "topics",
        [
            {"_id": bson.ObjectId(), "label": "topic-1", "query": "test", "user": user_ids[0], "topic_type": "wire"},
            {"_id": bson.ObjectId(), "label": "topic-2", "query": "mock", "user": user_ids[0], "topic_type": "agenda"},
        ],
    )

    async with client.session_transaction() as session:
        user = str(user_ids[0])
        session["user"] = user

    with app.mail.record_messages() as outbox:
        key = b"something random"
        app.config["PUSH_KEY"] = key
        data = {
            "guid": "foo",
            "type": "text",
            "headline": "this is a test",
            "service": [{"name": "Australian Weather", "code": "b"}],
        }
        headers = get_signature_headers(json.dumps(data), key)
        resp = await client.post("/push", json=data, headers=headers)
        assert 200 == resp.status_code
    assert len(outbox) == 0


@markers.requires_async_celery
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_send_notification_emails(client, app):
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

    async with client.session_transaction() as session:
        user = str(user_ids[0])
        session["user"] = user

    with app.mail.record_messages() as outbox:
        key = b"something random"
        app.config["PUSH_KEY"] = key
        data = {
            "guid": "foo",
            "type": "text",
            "headline": "this is a test headline",
            "byline": "John Smith",
            "slugline": "This is the main slugline",
            "description_text": "This is the main description text",
        }
        headers = get_signature_headers(json.dumps(data), key)
        resp = await client.post("/push", json=data, headers=headers)
        assert 200 == resp.status_code

    # TODO-ASYNC: len(outbox) is 0
    assert len(outbox) == 1
    assert "http://localhost:5050/wire?item=foo" in outbox[0].body


async def test_matching_topics(client, app):
    app.config["WIRE_AGGS"]["genre"] = {"terms": {"field": "genre.name", "size": 50}}
    await client.post("/push", json=item)
    search = get_resource_service("wire_search")

    user_id = ObjectId()
    company_id = ObjectId()
    users: dict[str, dict] = {
        str(user_id): UserResourceModel(
            id=user_id,
            email="foo@bar.org",
            first_name="foo",
            last_name="bar",
            user_type=UserRole.ADMINISTRATOR,
            company=company_id,
        ).to_dict(),
    }
    companies: dict[str, dict] = {
        str(company_id): CompanyResource(
            id=company_id,
            name="test-comp",
        ).to_dict(),
    }
    topic_ids = dict(
        created_to_old=ObjectId(),
        created_from_future=ObjectId(),
        filter=ObjectId(),
        query=ObjectId(),
    )
    topics = [
        {"_id": topic_ids["created_to_old"], "created": {"to": "2017-01-01"}, "user": user_id},
        {
            "_id": topic_ids["created_from_future"],
            "created": {"from": "now/d"},
            "user": user_id,
            "timezone_offset": 60 * 28,
        },
        {"_id": topic_ids["filter"], "filter": {"genre": ["other"]}, "user": user_id},
        {"_id": topic_ids["query"], "query": "Foo", "user": user_id},
    ]
    matching = search.get_matching_topics(item["guid"], topics, users, companies)
    assert [topic_ids["created_from_future"], topic_ids["query"]] == matching


async def test_matching_topics_for_public_user(client, app):
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
    await client.post("/push", json=item)
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


async def test_matching_topics_for_user_with_inactive_company(client, app):
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
    await client.post("/push", json=item)
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
    async with app.app_context():
        matching = search.get_matching_topics(item["guid"], topics, users, companies)
        assert ["created_from_future", "query"] == matching


async def test_push_parsed_item(client, app):
    await client.post("/push", json=item)
    parsed = get_entity_or_404(item["guid"], "wire_search")
    assert isinstance(parsed["firstcreated"], datetime)
    assert 2 == parsed["wordcount"]
    assert 7 == parsed["charcount"]


async def test_push_parsed_dates(client, app):
    payload = item.copy()
    payload["embargoed"] = "2019-01-31T00:01:00+00:00"
    await client.post("/push", json=payload)
    parsed = get_entity_or_404(item["guid"], "items")
    assert isinstance(parsed["firstcreated"], datetime)
    assert isinstance(parsed["versioncreated"], datetime)
    assert isinstance(parsed["embargoed"], datetime)


async def test_push_event_coverage_info(client, app):
    await client.post("/push", json=item)
    parsed = get_entity_or_404(item["guid"], "items")
    assert parsed["event_id"] == "urn:event/1"
    assert parsed["coverage_id"] == "urn:coverage/1"


async def test_push_wire_subject_whitelist(client, app):
    app.config["WIRE_SUBJECT_SCHEME_WHITELIST"] = ["b"]
    await client.post("/push", json=item)
    parsed = get_entity_or_404(item["guid"], "items")
    assert 1 == len(parsed["subject"])
    assert "b" == parsed["subject"][0]["name"]


async def test_push_custom_expiry(client, app):
    app.config["SOURCE_EXPIRY_DAYS"] = {"foo": 50}
    updated = item.copy()
    updated["source"] = "foo"
    await client.post("/push", json=updated)
    parsed = get_entity_or_404(item["guid"], "items")
    now = datetime.utcnow().replace(second=0, microsecond=0)
    expiry: datetime = parsed["expiry"].replace(tzinfo=None)
    assert now + timedelta(days=49) < expiry < now + timedelta(days=51)


async def test_matching_topics_with_mallformed_query(client, app):
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
    await client.post("/push", json=item)
    search = get_resource_service("wire_search")

    users = get_user_dict(use_globals=False)
    companies = get_company_dict(use_globals=False)
    topics = [
        {"_id": "good", "query": "*:*", "user": TEST_USER_ID},
        {"_id": "bad", "query": "AND Foo", "user": PUBLIC_USER_ID},
    ]
    async with app.app_context():
        matching = search.get_matching_topics(item["guid"], topics, users, companies)
        assert ["good"] == matching


async def test_matching_topics_when_disabling_section(client, app):
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

    await client.post("/push", json=item)
    search = get_resource_service("wire_search")

    users = get_user_dict(use_globals=False)
    companies = get_company_dict(use_globals=False)
    topics = [
        {"_id": "all wire", "query": "*:*", "user": TEST_USER_ID, "topic_type": "wire"},
        {"_id": "all agenda", "query": "*:*", "user": TEST_USER_ID, "topic_type": "agenda"},
    ]
    users[str(TEST_USER_ID)]["sections"] = {"wire": False, "agenda": True}
    async with app.app_context():
        matching = search.get_matching_topics(item["guid"], topics, users, companies)
        assert [] == matching
