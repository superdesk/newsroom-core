import io
import os
import hmac
import bson
from unittest import mock
from datetime import datetime, timedelta

from bson import ObjectId
from quart import json
from quart.datastructures import FileStorage

from newsroom.types import UserResourceModel, CompanyResource, UserRole, TopicResourceModel, SectionEnum
from newsroom.utils import get_company_dict_async, get_user_dict_async
from newsroom.wire import WireSearchServiceAsync
from newsroom.notifications import NotificationsService
from newsroom.history_async import HistoryService

from newsroom.tests.fixtures import TEST_USER_ID  # noqa - Fix cyclic import when running single test file
from newsroom.tests import markers
from tests.core.utils import add_company_products, create_entries_for, update_entries_for, find_one_by_id
from ..fixtures import COMPANY_1_ID, PUBLIC_USER_ID
from ..utils import mock_send_email, get_json


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
    user_ids = await create_entries_for(
        "auth_user",
        [
            {
                "email": "foo2@bar.com",
                "first_name": "Foo",
                "last_name": "Bar",
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
    push_mock = mocker.patch("newsroom.push.notifications.push_notification")

    data = {"guid": "foo", "type": "text", "headline": "this is a test"}
    headers = get_signature_headers(json.dumps(data), key)
    resp = await client.post("/push", json=data, headers=headers)
    assert 200 == resp.status_code

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
    company_ids = await create_entries_for(
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
        "last_name": "Bar",
        "is_enabled": True,
        "receive_email": True,
        "receive_app_notifications": True,
        "company": company_ids[0],
    }

    user_ids = await create_entries_for("auth_user", [user])
    user["_id"] = user_ids[0]

    await HistoryService().create_history_record(
        docs=[{"_id": "bar", "version": "1"}],
        action="download",
        user_id=user_ids[0],
        company_id=company_ids[0],
        section="wire",
    )

    with app.mail.record_messages() as outbox:
        key = b"something random"
        app.config["PUSH_KEY"] = key
        data = {"guid": "bar", "type": "text", "headline": "this is a test"}
        push_mock = mocker.patch("newsroom.notifications.utils.push_notification")
        headers = get_signature_headers(json.dumps(data), key)
        resp = await client.post("/push", json=data, headers=headers)
        assert 200 == resp.status_code

        assert push_mock.call_args[0][0] == "new_notifications"
        assert str(user_ids[0]) in push_mock.call_args[1]["counts"].keys()

        notification = await NotificationsService().find_one(user=user_ids[0])
        assert notification.action == "history_match"
        assert notification.item == "bar"
        assert notification.resource == "text"
        assert notification.user == user_ids[0]

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
    company_ids = await create_entries_for(
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
        "last_name": "Bar",
        "is_enabled": True,
        "receive_email": False,  # should still get email
        "receive_app_notifications": True,
        "company": company_ids[0],
    }

    user_ids = await create_entries_for("auth_user", [user])
    user["_id"] = user_ids[0]

    await HistoryService().create_history_record(
        docs=[{"_id": "bar", "version": "1"}],
        action="download",
        user_id=user_ids[0],
        company_id=company_ids[0],
        section="wire",
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
    push_mock = mocker.patch("newsroom.notifications.utils.push_notification")
    headers = get_signature_headers(json.dumps(data), key)

    with app.mail.record_messages() as outbox:
        resp = await client.post("/push", json=data, headers=headers)
        assert 200 == resp.status_code

        assert push_mock.call_args[0][0] == "new_notifications"
        assert str(user_ids[0]) in push_mock.call_args[1]["counts"].keys()
    assert len(outbox) == 1
    notification = await NotificationsService().find_one(user=user_ids[0])
    assert notification.action == "history_match"
    assert notification.item == "bar"
    assert notification.resource == "text"
    assert notification.user == user_ids[0]


@markers.requires_async_celery
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_notify_user_matches_for_new_item_in_bookmarks(client, app, mocker):
    user = {
        "email": "foo2@bar.com",
        "first_name": "Foo",
        "last_name": "Bar",
        "is_enabled": True,
        "is_approved": True,
        "receive_email": True,
        "receive_app_notifications": True,
        "company": COMPANY_1_ID,
    }

    user_ids = await create_entries_for("auth_user", [user])
    user["_id"] = user_ids[0]

    await add_company_products(
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

    await create_entries_for(
        "items",
        [
            {
                "_id": "bar",
                "headline": "testing",
                "service": [{"code": "a", "name": "Service A"}],
                "products": [{"code": "product-1", "name": "product-1"}],
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
        push_mock = mocker.patch("newsroom.notifications.utils.push_notification")
        headers = get_signature_headers(json.dumps(data), key)
        resp = await client.post("/push", json=data, headers=headers)
        assert 200 == resp.status_code

        assert push_mock.call_args[0][0] == "new_notifications"
        assert str(user_ids[0]) in push_mock.call_args[1]["counts"].keys()

        notification = await NotificationsService().find_one(user=user_ids[0])
        assert notification.action == "history_match"
        assert notification.item == "bar"
        assert notification.resource == "text"
        assert notification.user == user_ids[0]

    assert len(outbox) == 1
    assert "http://localhost:5050/wire?item=bar" in outbox[0].body


@markers.requires_async_celery
async def test_do_not_notify_disabled_user(client, app, mocker):
    company_ids = await create_entries_for(
        "companies",
        [
            {
                "name": "Press 2 co.",
                "is_enabled": True,
            }
        ],
    )

    user_ids = await create_entries_for(
        "auth_user",
        [
            {
                "email": "foo2@bar.com",
                "first_name": "Foo",
                "last_name": "Bar",
                "is_enabled": True,
                "receive_email": True,
                "company": company_ids[0],
            }
        ],
    )

    async with client.session_transaction() as session:
        user = str(user_ids[0])
        session["user"] = user
    resp = await client.post(
        "users/%s/topics" % user,
        json={"label": "bar", "topic_type": "wire", "query": "test", "notifications": True},
    )
    assert 201 == resp.status_code, await resp.get_data(as_text=True)

    # disable user
    user = await find_one_by_id("users", user_ids[0])
    await update_entries_for("users", user_ids[0], {"is_enabled": False}, user)
    # clean cache
    app.cache.delete(str(user_ids[0]))

    key = b"something random"
    app.config["PUSH_KEY"] = key
    data = {"guid": "foo", "type": "text", "headline": "this is a test"}
    push_mock = mocker.patch("newsroom.push.notifications.push_notification")
    headers = get_signature_headers(json.dumps(data), key)
    resp = await client.post("/push", json=data, headers=headers)
    assert 200 == resp.status_code
    assert push_mock.call_args[1]["_items"][0]["_id"] == "foo"


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_notify_checks_service_subscriptions(client, app, mocker):
    company_id = ObjectId()
    await create_entries_for(
        "companies",
        [
            {
                "_id": company_id,
                "name": "Press 2 co.",
                "is_enabled": True,
            }
        ],
    )

    user_ids = await create_entries_for(
        "auth_user",
        [
            {
                "email": "foo2@bar.com",
                "first_name": "Foo",
                "last_name": "Bar",
                "is_enabled": True,
                "receive_email": True,
                "company": company_id,
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
        assert 200 == resp.status_code, await resp.get_data(as_text=True)
    assert len(outbox) == 0


@markers.requires_async_celery
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_send_notification_emails(client, app):
    user_ids = await create_entries_for(
        "auth_user",
        [
            {
                "email": "foo2@bar.com",
                "first_name": "Foo",
                "last_name": "Bar",
                "is_enabled": True,
                "receive_email": True,
                "user_type": "administrator",
            }
        ],
    )

    await create_entries_for(
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

    assert len(outbox) == 1
    assert "http://localhost:5050/wire?item=foo" in outbox[0].body


async def test_matching_topics(client, app):
    app.config["WIRE_AGGS"]["genre"] = {"terms": {"field": "genre.name", "size": 50}}
    await client.post("/push", json=item)

    user_id = ObjectId()
    company_id = ObjectId()
    users: list[UserResourceModel] = [
        UserResourceModel(
            id=user_id,
            email="foo@bar.org",
            first_name="foo",
            last_name="bar",
            user_type=UserRole.ADMINISTRATOR,
            company=company_id,
        )
    ]
    companies: dict[ObjectId, CompanyResource] = {
        company_id: CompanyResource(
            id=company_id,
            name="test-comp",
            sections={"wire": True},
        ),
    }
    topic_ids = dict(
        created_to_old=ObjectId(),
        created_from_future=ObjectId(),
        filter=ObjectId(),
        query=ObjectId(),
    )
    topics: list[TopicResourceModel] = [
        TopicResourceModel.from_dict(
            dict(
                _id=topic_ids["created_to_old"],
                _created=None,
                label="Created - Too old",
                created={"to": "2017-01-01"},
                user=user_id,
                topic_type=SectionEnum.WIRE,
            )
        ),
        TopicResourceModel.from_dict(
            dict(
                _id=topic_ids["created_from_future"],
                _created=None,
                label="Created - From future",
                created={"from": "now/d"},
                timezone_offset=60 * 28,
                user=user_id,
                topic_type=SectionEnum.WIRE,
            )
        ),
        TopicResourceModel.from_dict(
            dict(
                _id=topic_ids["filter"],
                _created=None,
                label="Filter",
                filter={"genre": ["other"]},
                user=user_id,
                topic_type=SectionEnum.WIRE,
            )
        ),
        TopicResourceModel.from_dict(
            dict(
                _id=topic_ids["query"],
                _created=None,
                label="Query",
                query="Foo",
                user=user_id,
                topic_type=SectionEnum.WIRE,
            )
        ),
    ]
    matching = await WireSearchServiceAsync().get_matching_topics_for_item(item["guid"], topics, users, companies)
    assert {topic_ids["created_from_future"], topic_ids["query"]} == matching


async def test_matching_topics_for_public_user(client, app):
    app.config["WIRE_AGGS"]["genre"] = {"terms": {"field": "genre.name", "size": 50}}
    await add_company_products(
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

    item["products"] = [{"code": "p-1", "name": "Sport"}]
    await client.post("/push", json=item)

    users = await get_user_dict_async(use_globals=False)
    assert PUBLIC_USER_ID in users
    companies = await get_company_dict_async(use_globals=False)
    topic_ids = dict(
        created_to_old=ObjectId(),
        created_from_future=ObjectId(),
        filter=ObjectId(),
        query=ObjectId(),
    )
    topics: list[TopicResourceModel] = [
        TopicResourceModel.from_dict(
            dict(
                _id=topic_ids["created_to_old"],
                _created=None,
                label="Created - Too old",
                created={"to": "2017-01-01"},
                user=PUBLIC_USER_ID,
                topic_type=SectionEnum.WIRE,
            )
        ),
        TopicResourceModel.from_dict(
            dict(
                _id=topic_ids["created_from_future"],
                _created=None,
                label="Created - From future",
                created={"from": "now/d"},
                timezone_offset=60 * 28,
                user=PUBLIC_USER_ID,
                topic_type=SectionEnum.WIRE,
            )
        ),
        TopicResourceModel.from_dict(
            dict(
                _id=topic_ids["filter"],
                _created=None,
                label="Filter",
                filter={"genre": ["other"]},
                user=PUBLIC_USER_ID,
                topic_type=SectionEnum.WIRE,
            )
        ),
        TopicResourceModel.from_dict(
            dict(
                _id=topic_ids["query"],
                _created=None,
                label="Query",
                query="Foo",
                user=PUBLIC_USER_ID,
                topic_type=SectionEnum.WIRE,
            )
        ),
    ]
    matching = await WireSearchServiceAsync().get_matching_topics_for_item(
        item["guid"], topics, list(users.values()), companies
    )
    assert {topic_ids["created_from_future"], topic_ids["query"]} == matching


async def test_matching_topics_for_user_with_inactive_company(client, app):
    app.config["WIRE_AGGS"]["genre"] = {"terms": {"field": "genre.name", "size": 50}}
    await add_company_products(
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

    item["products"] = [{"code": "p-1", "name": "Sport"}]
    await client.post("/push", json=item)

    users = await get_user_dict_async(use_globals=False)
    companies = await get_company_dict_async(use_globals=False)
    topic_ids = dict(
        created_to_old=ObjectId(),
        created_from_future=ObjectId(),
        filter=ObjectId(),
        query=ObjectId(),
    )
    topics: list[TopicResourceModel] = [
        TopicResourceModel.from_dict(
            dict(
                _id=topic_ids["created_to_old"],
                _created=None,
                label="Created - Too old",
                created={"to": "2017-01-01"},
                user=ObjectId(),
                topic_type=SectionEnum.WIRE,
            )
        ),
        TopicResourceModel.from_dict(
            dict(
                _id=topic_ids["created_from_future"],
                _created=None,
                label="Created - From future",
                created={"from": "now/d"},
                timezone_offset=60 * 28,
                user=PUBLIC_USER_ID,
                topic_type=SectionEnum.WIRE,
            )
        ),
        TopicResourceModel.from_dict(
            dict(
                _id=topic_ids["filter"],
                _created=None,
                label="Filter",
                filter={"genre": ["other"]},
                user=ObjectId(),
                topic_type=SectionEnum.WIRE,
            )
        ),
        TopicResourceModel.from_dict(
            dict(
                _id=topic_ids["query"],
                _created=None,
                label="Query",
                query="Foo",
                user=PUBLIC_USER_ID,
                topic_type=SectionEnum.WIRE,
            )
        ),
    ]
    matching = await WireSearchServiceAsync().get_matching_topics_for_item(
        item["guid"], topics, list(users.values()), companies
    )
    assert {topic_ids["created_from_future"], topic_ids["query"]} == matching


async def test_push_parsed_item(client, app):
    await client.post("/push", json=item)
    parsed = await find_one_by_id("items", item["guid"])
    assert isinstance(parsed["firstcreated"], datetime)
    assert 2 == parsed["wordcount"]
    assert 7 == parsed["charcount"]


async def test_push_parsed_dates(client, app):
    payload = item.copy()
    payload["embargoed"] = "2019-01-31T00:01:00+00:00"
    await client.post("/push", json=payload)
    parsed = await find_one_by_id("items", item["guid"])
    assert isinstance(parsed["firstcreated"], datetime)
    assert isinstance(parsed["versioncreated"], datetime)
    assert isinstance(parsed["embargoed"], datetime)


async def test_push_event_coverage_info(client, app):
    await client.post("/push", json=item)
    parsed = await find_one_by_id("items", item["guid"])
    assert parsed["event_id"] == "urn:event/1"
    assert parsed["coverage_id"] == "urn:coverage/1"


async def test_push_wire_subject_whitelist(client, app):
    app.config["WIRE_SUBJECT_SCHEME_WHITELIST"] = ["b"]
    await client.post("/push", json=item)
    parsed = await find_one_by_id("items", item["guid"])
    assert 1 == len(parsed["subject"])
    assert "b" == parsed["subject"][0]["name"]


async def test_push_custom_expiry(client, app):
    app.config["SOURCE_EXPIRY_DAYS"] = {"foo": 50}
    updated = item.copy()
    updated["source"] = "foo"
    await client.post("/push", json=updated)
    parsed = await find_one_by_id("items", item["guid"])
    now = datetime.utcnow().replace(second=0, microsecond=0)
    expiry: datetime = parsed["expiry"].replace(tzinfo=None)
    assert now + timedelta(days=49) < expiry < now + timedelta(days=51)


async def test_matching_topics_with_mallformed_query(client, app):
    await add_company_products(
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

    item["products"] = [{"code": "p-1", "name": "Sport"}]
    await client.post("/push", json=item)

    users = await get_user_dict_async(use_globals=False)
    companies = await get_company_dict_async(use_globals=False)
    topic_ids = dict(
        good=ObjectId(),
        bad=ObjectId(),
    )
    topics: list[TopicResourceModel] = [
        TopicResourceModel.from_dict(
            dict(
                _id=topic_ids["good"],
                _created=None,
                label="Good",
                user=TEST_USER_ID,
                topic_type=SectionEnum.WIRE,
                query="*:*",
            )
        ),
        TopicResourceModel.from_dict(
            dict(
                _id=topic_ids["bad"],
                _created=None,
                label="Bad",
                user=PUBLIC_USER_ID,
                topic_type=SectionEnum.WIRE,
                query="AND Foo",
            )
        ),
    ]

    matching = await WireSearchServiceAsync().get_matching_topics_for_item(
        item["guid"], topics, list(users.values()), companies
    )
    assert {topic_ids["good"]} == matching


async def test_matching_topics_when_disabling_section(client, app):
    await add_company_products(
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

    users = await get_user_dict_async(use_globals=False)
    companies = await get_company_dict_async(use_globals=False)
    topic_ids = dict(
        all_wire=ObjectId(),
        all_agenda=ObjectId(),
    )
    topics: list[TopicResourceModel] = [
        TopicResourceModel.from_dict(
            dict(
                _id=topic_ids["all_wire"],
                _created=None,
                label="All Wire",
                user=TEST_USER_ID,
                topic_type=SectionEnum.WIRE,
                query="*:*",
            )
        ),
        TopicResourceModel.from_dict(
            dict(
                _id=topic_ids["all_agenda"],
                _created=None,
                label="All Agenda",
                user=TEST_USER_ID,
                topic_type=SectionEnum.AGENDA,
                query="*:*",
            )
        ),
    ]
    users[TEST_USER_ID].sections = {"wire": False, "agenda": True}
    matching = await WireSearchServiceAsync().get_matching_topics_for_item(
        item["guid"], topics, list(users.values()), companies
    )
    assert set() == matching


# CPCN-967
async def test_global_topic_after_deleting_user(client, app):
    await add_company_products(
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

    users = await get_user_dict_async(use_globals=False)
    companies = await get_company_dict_async(use_globals=False)
    topic_id = ObjectId()
    topic = TopicResourceModel.from_dict(
        dict(
            _id=topic_id,
            _created=None,
            label="All Wire",
            query="*:*",
            user=None,
            topic_type=SectionEnum.WIRE,
            subscribers=[{"user_id": TEST_USER_ID, "notification_type": "real-time"}],
        )
    )
    matching = await WireSearchServiceAsync().get_matching_topics_for_item(
        item["guid"], [topic], list(users.values()), companies
    )
    assert matching == {topic_id}


# STT-51
async def test_planning_to_many_events(client, app):
    event_item_1 = {
        "_id": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c168",
        "type": "event",
        "occur_status": {
            "qcode": "eocstat:eos5",
            "name": "Planned, occurs certainly",
            "label": "Planned, occurs certainly",
        },
        "dates": {"start": "2024-11-14T18:30:00+0000", "end": "2024-11-15T18:29:59+0000", "tz": "Asia/Calcutta"},
        "calendars": [{"name": "Sport", "qcode": "sport"}],
        "state": "scheduled",
        "language": "en",
        "name": "Event1",
        "_updated": "2024-11-15T09:51:44+0000",
        "_created": "2024-11-15T09:50:57+0000",
        "guid": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c168",
        "firstcreated": "2024-11-15T09:50:57+0000",
        "versioncreated": "2024-11-15T09:51:44+0000",
        "pubstatus": "usable",
        "version_creator": "66e13583bf2361cacc440666",
        "item_id": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c168",
        "products": [{"code": "6715cb9a62f7204f57cc0ea5", "name": "news"}],
    }

    await client.post("/push", json=event_item_1)

    event_item_2 = {
        "_id": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c169",
        "type": "event",
        "occur_status": {
            "qcode": "eocstat:eos5",
            "name": "Planned, occurs certainly",
            "label": "Planned, occurs certainly",
        },
        "dates": {"start": "2024-11-14T18:30:00+0000", "end": "2024-11-15T18:29:59+0000", "tz": "Asia/Calcutta"},
        "calendars": [{"name": "Sport", "qcode": "sport"}],
        "state": "scheduled",
        "language": "en",
        "name": "Event2",
        "_updated": "2024-11-15T09:51:44+0000",
        "_created": "2024-11-15T09:50:57+0000",
        "guid": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c169",
        "firstcreated": "2024-11-15T09:50:57+0000",
        "versioncreated": "2024-11-15T09:51:44+0000",
        "pubstatus": "usable",
        "version_creator": "66e13583bf2361cacc440666",
        "item_id": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c169",
        "products": [{"code": "6715cb9a62f7204f57cc0ea5", "name": "news"}],
    }

    await client.post("/push", json=event_item_2)

    planning_item = {
        "_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b9ad",
        "state": "scheduled",
        "type": "planning",
        "planning_date": "2024-11-14T18:30:00+0000",
        "event_item": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c169",
        "related_events": [
            {
                "_id": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c168",
                "link_type": "secondary",
            }
        ],
        "coverages": [
            {
                "firstcreated": "2024-11-15T09:51:44+0000",
                "versioncreated": "2024-11-15T09:51:44+0000",
                "news_coverage_status": {"qcode": "ncostat:int", "name": "coverage intended", "label": "Planned"},
                "workflow_status": "draft",
                "planning": {"language": "nl", "g2_content_type": "text", "scheduled": "2024-11-15T10:30:00+0000"},
                "coverage_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.625299:4ebaa306-a03e-4cd7-8454-ad65cc9c6e77",
                "original_coverage_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.625299:4ebaa306-a03e-4cd7-8454-ad65cc9c6e77",
                "assigned_user": {"first_name": "None", "last_name": "None", "display_name": "1admin"},
                "assigned_desk": {"name": "Sports Desk"},
                "coverage_provider": {"name": "Stringer"},
            }
        ],
        "name": "Planning many",
        "guid": "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b9ad",
        "language": "en",
        "firstcreated": "2024-11-15T09:51:44+0000",
        "versioncreated": "2024-11-15T09:52:20+0000",
        "pubstatus": "usable",
        "versionposted": "2024-11-15T09:52:20+0000",
        "state_reason": "None",
        "item_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b9ad",
        "products": [{"code": "6715cb9a62f7204f57cc0ea5", "name": "news"}],
        "events": [
            {
                "rel": "secondary",
                "uri": "urn:event:urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c168",
                "literal": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c168",
                "name": "Event1",
            }
        ],
    }

    await client.post("/push", json=planning_item)
    events = await get_json(client, "/agenda/search")

    # Primary link event with coverages
    eitem1 = events["_items"][1]
    assert eitem1["_id"] == "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c169"
    assert eitem1["item_type"] == "event"
    assert eitem1["planning_ids"] == [
        "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b9ad"
    ]
    assert len(eitem1["coverages"]) == 1

    # secondary link event with coverages
    eitem2 = events["_items"][2]
    assert eitem2["_id"] == "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c168"
    assert eitem2["item_type"] == "event"
    assert len(eitem2["coverages"]) == 1
    assert (
        eitem2["planning_ids"][0]
        == "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b9ad"
    )
    assert eitem2["planning_items"] == []


async def test_planning_to_many_events_duplicate_coverages(client, app):
    event = {
        "_id": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c170",
        "type": "event",
        "occur_status": {
            "qcode": "eocstat:eos5",
            "name": "Planned, occurs certainly",
            "label": "Planned, occurs certainly",
        },
        "dates": {"start": "2024-11-14T18:30:00+0000", "end": "2024-11-15T18:29:59+0000", "tz": "Asia/Calcutta"},
        "calendars": [{"name": "Sport", "qcode": "sport"}],
        "state": "scheduled",
        "language": "en",
        "name": "Event1",
        "_updated": "2024-11-15T09:51:44+0000",
        "_created": "2024-11-15T09:50:57+0000",
        "guid": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c170",
        "firstcreated": "2024-11-15T09:50:57+0000",
        "versioncreated": "2024-11-15T09:51:44+0000",
        "version_creator": "66e13583bf2361cacc440666",
        "item_id": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c170",
        "products": [{"code": "6715cb9a62f7204f57cc0ea5", "name": "news"}],
    }

    await client.post("/push", json=event)

    planning_item_1 = {
        "_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b985",
        "item_class": "plinat:newscoverage",
        "state": "scheduled",
        "type": "planning",
        "planning_date": "2024-11-14T18:30:00+0000",
        "related_events": [
            {
                "_id": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c170",
                "link_type": "secondary",
            }
        ],
        "coverages": [
            {
                "firstcreated": "2024-11-15T09:51:44+0000",
                "versioncreated": "2024-11-15T09:51:44+0000",
                "news_coverage_status": {"qcode": "ncostat:int", "name": "coverage intended", "label": "Planned"},
                "workflow_status": "draft",
                "planning": {"language": "nl", "g2_content_type": "text", "scheduled": "2024-11-15T10:30:00+0000"},
                "coverage_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.625299:4ebaa306-a03e-4cd7-8454-ad65cc9c6e76",
                "original_coverage_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.625299:4ebaa306-a03e-4cd7-8454-ad65cc9c6e76",
                "assigned_user": {"first_name": "None", "last_name": "None", "display_name": "1admin"},
                "assigned_desk": {"name": "Sports Desk"},
                "coverage_provider": {"name": "Stringer_one"},
            }
        ],
        "name": "Planning many One",
        "guid": "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b985",
        "language": "en",
        "firstcreated": "2024-11-15T09:51:44+0000",
        "versioncreated": "2024-11-15T09:52:20+0000",
        "_created": "2024-11-15T09:51:44+0000",
        "_updated": "2024-11-15T09:52:20+0000",
        "pubstatus": "usable",
        "versionposted": "2024-11-15T09:52:20+0000",
        "state_reason": "None",
        "item_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b985",
        "products": [{"code": "6715cb9a62f7204f57cc0ea5", "name": "news"}],
        "events": [
            {
                "rel": "secondary",
                "uri": "urn:event:urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c170",
                "literal": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c170",
                "name": "Event1",
            }
        ],
    }

    await client.post("/push", json=planning_item_1)

    planning_item_2 = {
        "_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b986",
        "agendas": [],
        "item_class": "plinat:newscoverage",
        "state": "scheduled",
        "type": "planning",
        "planning_date": "2024-11-14T18:30:00+0000",
        "related_events": [
            {
                "_id": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c170",
                "link_type": "secondary",
            }
        ],
        "coverages": [
            {
                "firstcreated": "2024-11-15T09:51:44+0000",
                "versioncreated": "2024-11-15T09:51:44+0000",
                "news_coverage_status": {"qcode": "ncostat:int", "name": "coverage intended", "label": "Planned"},
                "workflow_status": "draft",
                "planning": {"language": "nl", "g2_content_type": "text", "scheduled": "2024-11-15T10:30:00+0000"},
                "coverage_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.625299:4ebaa306-a03e-4cd7-8454-ad65cc9c6e78",
                "original_coverage_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.625299:4ebaa306-a03e-4cd7-8454-ad65cc9c6e78",
                "assigned_user": {"first_name": "None", "last_name": "None", "display_name": "1admin"},
                "assigned_desk": {"name": "Sports Desk"},
                "coverage_provider": {"name": "Stringer_Two"},
            }
        ],
        "name": "Planning many One",
        "guid": "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b986",
        "language": "en",
        "firstcreated": "2024-11-15T09:51:44+0000",
        "versioncreated": "2024-11-15T09:52:20+0000",
        "_created": "2024-11-15T09:51:44+0000",
        "_updated": "2024-11-15T09:52:20+0000",
        "versionposted": "2024-11-15T09:52:20+0000",
        "item_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b986",
        "products": [{"code": "6715cb9a62f7204f57cc0ea5", "name": "news"}],
        "events": [
            {
                "rel": "secondary",
                "uri": "urn:event:urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c170",
                "literal": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c170",
                "name": "Event1",
            }
        ],
    }

    await client.post("/push", json=planning_item_2)

    events = await get_json(client, "/agenda/search")

    # assert events_ids populated in the planning Item
    assert (
        events["_items"][1]["_id"]
        == "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b985"
    )
    assert events["_items"][1]["item_type"] == "planning"
    assert events["_items"][1]["event_ids"] == [
        "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c170"
    ]

    assert (
        events["_items"][2]["_id"]
        == "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b986"
    )
    assert events["_items"][2]["item_type"] == "planning"
    assert events["_items"][2]["event_ids"] == [
        "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c170"
    ]

    # assert planning_ids and coverages are populated in the Event Item
    assert events["_items"][3]["planning_ids"] == [
        "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b985",
        "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b986",
    ]
    assert len(events["_items"][3]["coverages"]) == 2
    assert (
        events["_items"][3]["coverages"][0]["coverage_id"]
        == "urn:newsml:localhost:5000:2024-11-15T15:21:44.625299:4ebaa306-a03e-4cd7-8454-ad65cc9c6e76"
    )
    assert (
        events["_items"][3]["coverages"][1]["coverage_id"]
        == "urn:newsml:localhost:5000:2024-11-15T15:21:44.625299:4ebaa306-a03e-4cd7-8454-ad65cc9c6e78"
    )

    # update coverages in existing planning_item
    planning_item_2 = {
        "_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b986",
        "item_class": "plinat:newscoverage",
        "state": "scheduled",
        "type": "planning",
        "planning_date": "2024-11-14T18:30:00+0000",
        "related_events": [
            {
                "_id": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c170",
                "link_type": "secondary",
            }
        ],
        "coverages": [
            {
                "firstcreated": "2024-11-15T09:51:44+0000",
                "versioncreated": "2024-11-15T09:51:44+0000",
                "news_coverage_status": {"qcode": "ncostat:int", "name": "coverage intended", "label": "Planned"},
                "workflow_status": "draft",
                "planning": {"language": "nl", "g2_content_type": "text", "scheduled": "2024-11-15T10:30:00+0000"},
                "coverage_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.625299:4ebaa306-a03e-4cd7-8454-ad65cc9c6e78",
                "original_coverage_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.625299:4ebaa306-a03e-4cd7-8454-ad65cc9c6e78",
                "assigned_user": {"first_name": "None", "last_name": "None", "display_name": "1admin"},
                "assigned_desk": {"name": "Sports Desk"},
                "coverage_provider": {"name": "Stringer_Two"},
            },
            {
                "firstcreated": "2024-11-15T09:51:44+0000",
                "versioncreated": "2024-11-15T09:51:44+0000",
                "news_coverage_status": {"qcode": "ncostat:int", "name": "coverage intended", "label": "Planned"},
                "workflow_status": "draft",
                "planning": {"language": "nl", "g2_content_type": "text", "scheduled": "2024-11-15T10:30:00+0000"},
                "coverage_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.625299:4ebaa306-a03e-4cd7-8454-ad65cc9c6e70",
                "original_coverage_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.625299:4ebaa306-a03e-4cd7-8454-ad65cc9c6e70",
                "assigned_user": {"first_name": "None", "last_name": "None", "display_name": "1admin"},
                "assigned_desk": {"name": "Sports Desk"},
                "coverage_provider": {"name": "Stringer_Two_updated"},
            },
        ],
        "name": "Planning many One",
        "guid": "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b986",
        "language": "en",
        "firstcreated": "2024-11-15T09:51:44+0000",
        "versioncreated": "2024-11-15T09:52:20+0000",
        "_created": "2024-11-15T09:51:44+0000",
        "_updated": "2024-11-15T09:52:20+0000",
        "pubstatus": "usable",
        "versionposted": "2024-11-15T09:55:20+0000",
        "item_id": "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b986",
        "products": [{"code": "6715cb9a62f7204f57cc0ea5", "name": "news"}],
        "events": [
            {
                "rel": "secondary",
                "uri": "urn:event:urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c170",
                "literal": "urn:newsml:localhost:5000:2024-11-15T15:20:57.904056:bcf346bd-3f59-4b28-87c1-4a5bb324c170",
                "name": "Event1",
            }
        ],
    }

    await client.post("/push", json=planning_item_2)

    events = await get_json(client, "/agenda/search")

    assert events["_items"][3]["planning_ids"] == [
        "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b985",
        "urn:newsml:localhost:5000:2024-11-15T15:21:44.624942:c734e329-c43b-4acd-991b-a53e1769b986",
    ]
    assert len(events["_items"][3]["coverages"]) == 3
    assert (
        events["_items"][3]["coverages"][0]["coverage_id"]
        == "urn:newsml:localhost:5000:2024-11-15T15:21:44.625299:4ebaa306-a03e-4cd7-8454-ad65cc9c6e76"
    )
    assert (
        events["_items"][3]["coverages"][1]["coverage_id"]
        == "urn:newsml:localhost:5000:2024-11-15T15:21:44.625299:4ebaa306-a03e-4cd7-8454-ad65cc9c6e78"
    )
    assert (
        events["_items"][3]["coverages"][2]["coverage_id"]
        == "urn:newsml:localhost:5000:2024-11-15T15:21:44.625299:4ebaa306-a03e-4cd7-8454-ad65cc9c6e70"
    )
