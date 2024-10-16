from pytest import fixture

from quart import json
from unittest import mock
from copy import deepcopy
from bson import ObjectId
import pymongo

from newsroom.types import UserResourceModel, TopicResourceModel, TopicType
from newsroom.topics.views import get_topic_url
from newsroom.users.service import UsersService
from ..fixtures import (  # noqa: F401
    PUBLIC_USER_NAME,
    PUBLIC_USER_EMAIL,
    init_company,
    PUBLIC_USER_ID,
    TEST_USER_ID,
    COMPANY_1_ID,
)
from ..utils import mock_send_email, get_resource_by_id  # noqa
from tests import utils
from tests.core.utils import create_entries_for
from newsroom.topics.topics_async import TopicService
from newsroom.topics_folders.folders import UserFoldersResourceService

WIRE_NAV_ID = ObjectId("5cc94454bc43165c045ffec9")
AGENDA_NAV_ID = ObjectId("5cc94454bc43165c045ffec0")

base_topic = {
    "_id": ObjectId(),
    "label": "Foo",
    "query": "foo",
    "topic_type": "wire",
    "navigation": [WIRE_NAV_ID],
}

agenda_topic = {
    "_id": ObjectId(),
    "label": "Foo",
    "query": "foo",
    "topic_type": "agenda",
    "navigation": [AGENDA_NAV_ID],
}

user_id = str(PUBLIC_USER_ID)
test_user_id = str(TEST_USER_ID)
topics_url = "users/%s/topics" % user_id

user_topic_folders_url = "/api/users/{}/topic_folders".format(TEST_USER_ID)
company_topic_folders_url = "/api/companies/{}/topic_folders".format(COMPANY_1_ID)


@fixture
async def navigation_items():
    await create_entries_for(
        "navigations",
        [
            {
                "_id": WIRE_NAV_ID,
                "name": "Foo",
                "product_type": "wire",
                "is_enabled": True,
            },
            {
                "_id": AGENDA_NAV_ID,
                "name": "Foo",
                "product_type": "agenda",
                "is_enabled": True,
            },
        ],
    )


async def test_topics_no_session(app):
    async with app.test_client() as client:
        resp = await client.get(topics_url)
        assert 302 == resp.status_code
        resp = await client.post(topics_url, data=deepcopy(base_topic))
        assert 302 == resp.status_code


async def test_post_topic_user(client, navigation_items):
    await utils.login_public(client)
    resp = await client.post(topics_url, json=deepcopy(base_topic))
    assert 201 == resp.status_code
    resp = await client.get(topics_url)
    assert 200 == resp.status_code
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])


async def test_update_topic_fails_for_different_user(app, client, navigation_items):
    topic = deepcopy(base_topic)
    topic_id = (await create_entries_for("topics", [topic]))[0]

    await utils.login(client, {"email": "test@bar.com"})
    resp = await client.post(f"topics/{topic_id}", json={"label": "test123"})
    assert 403 == resp.status_code


async def test_update_topic(client, navigation_items):
    await utils.login_public(client)
    resp = await client.post(topics_url, json=deepcopy(base_topic))
    assert 201 == resp.status_code

    resp = await client.get(topics_url)
    data = json.loads(await resp.get_data())
    _id = data["_items"][0]["_id"]

    resp = await client.post(
        "topics/{}".format(_id),
        json={"label": "test123"},
    )
    assert 200 == resp.status_code  # , await resp.get_data(as_text=True)

    resp = await client.get(topics_url)
    data = json.loads(await resp.get_data())
    assert "test123" == data["_items"][0]["label"]


async def test_delete_topic(client, navigation_items):
    await utils.login(client, {"email": PUBLIC_USER_EMAIL})
    resp = await client.post(topics_url, json=deepcopy(base_topic))
    assert 201 == resp.status_code

    resp = await client.get(topics_url)
    data = json.loads(await resp.get_data())
    _id = data["_items"][0]["_id"]

    resp = await client.delete("topics/{}".format(_id))
    assert 200 == resp.status_code

    resp = await client.get(topics_url)
    data = json.loads(await resp.get_data())
    assert 0 == len(data["_items"])


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_share_wire_topics(client, app, navigation_items):
    topic = deepcopy(base_topic)
    topic_ids = await create_entries_for("topics", [topic])
    topic["_id"] = topic_ids[0]
    await utils.login(client, {"email": PUBLIC_USER_EMAIL})

    with app.mail.record_messages() as outbox:
        resp = await client.post(
            "/topic_share",
            json={
                "items": topic,
                "users": [test_user_id],
                "message": "Some info message",
            },
        )

        assert resp.status_code == 201, (await resp.get_data()).decode("utf-8")
        assert len(outbox) == 1
        assert outbox[0].recipients == ["test@bar.com"]
        assert outbox[0].sender == "newsroom@localhost"
        assert outbox[0].subject == "From Newshub: %s" % topic["label"]
        assert "Hi Test Bar" in outbox[0].body
        assert "Foo Bar (foo@bar.com) shared " in outbox[0].body
        assert topic["query"] in outbox[0].body
        assert "Some info message" in outbox[0].body
        assert "/wire" in outbox[0].body


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_share_agenda_topics(client, app, navigation_items):
    topic_ids = await create_entries_for("topics", [agenda_topic])
    agenda_topic["_id"] = topic_ids[0]
    await utils.login(client, {"email": PUBLIC_USER_EMAIL})

    with app.mail.record_messages() as outbox:
        resp = await client.post(
            "/topic_share",
            json={
                "items": agenda_topic,
                "users": [test_user_id],
                "message": "Some info message",
            },
        )

        assert resp.status_code == 201, (await resp.get_data()).decode("utf-8")
        assert len(outbox) == 1
        assert outbox[0].recipients == ["test@bar.com"]
        assert outbox[0].sender == "newsroom@localhost"
        assert outbox[0].subject == "From Newshub: %s" % agenda_topic["label"]
        assert "Hi Test Bar" in outbox[0].body
        assert "Foo Bar (foo@bar.com) shared " in outbox[0].body
        assert agenda_topic["query"] in outbox[0].body
        assert "Some info message" in outbox[0].body
        assert "/agenda" in outbox[0].body


async def test_get_topic_share_url(app):
    topic = TopicResourceModel(id=ObjectId(), label="Test Topic", topic_type=TopicType.WIRE, query="art exhibition")
    assert get_topic_url(topic) == "http://localhost:5050/wire?q=art+exhibition"

    topic.query = None
    topic.filter = {"location": [["Sydney"]]}
    assert get_topic_url(topic) == "http://localhost:5050/wire?filter=%7B%22location%22:+%5B%5B%22Sydney%22%5D%5D%7D"

    topic.filter = None
    NAV1_ID = ObjectId()
    NAV2_ID = ObjectId()
    topic.navigation = [NAV1_ID]
    assert get_topic_url(topic) == f"http://localhost:5050/wire?navigation=%5B%22{NAV1_ID}%22%5D"

    topic.navigation = [NAV1_ID, NAV2_ID]
    assert get_topic_url(topic) == f"http://localhost:5050/wire?navigation=%5B%22{NAV1_ID}%22,+%22{NAV2_ID}%22%5D"

    topic.navigation = None
    topic.created_filter = {"from": "2018-06-01"}
    assert get_topic_url(topic) == "http://localhost:5050/wire?created=%7B%22from%22:+%222018-06-01%22%7D"

    topic.created_filter = None
    topic.advanced = {"all": "Weather Sydney", "fields": ["headline", "body_html"]}
    assert get_topic_url(topic) == (
        "http://localhost:5050/wire?advanced="
        "%7B%22all%22:+%22Weather+Sydney%22,+%22fields%22:+%5B%22headline%22,+%22body_html%22%5D%7D"
    )

    topic = TopicResourceModel(
        id=ObjectId(),
        label="Test Topic",
        topic_type=TopicType.WIRE,
        query="art exhibition",
        filter={"urgency": [3]},
        navigation=[NAV1_ID],
        created_filter={"from": "2018-06-01"},
        advanced={"all": "Weather Sydney", "fields": ["headline", "body_html"]},
    )
    assert (
        get_topic_url(topic) == "http://localhost:5050/wire?"
        "q=art+exhibition"
        "&filter=%7B%22urgency%22:+%5B3%5D%7D"
        f"&navigation=%5B%22{NAV1_ID}%22%5D"
        "&created=%7B%22from%22:+%222018-06-01%22%7D"
        "&advanced=%7B%22all%22:+%22Weather+Sydney%22,+%22fields%22:+%5B%22headline%22,+%22body_html%22%5D%7D"
    )


def self_href(doc):
    return "api/{}".format(doc["_links"]["self"]["href"])


def if_match(doc):
    return {"if-match": doc["_etag"]}


async def test_topic_folders_crud(client):
    await utils.login(client, {"email": PUBLIC_USER_EMAIL})
    urls = (user_topic_folders_url, company_topic_folders_url)
    for folders_url in urls:
        folder = {"name": "test", "section": "wire"}

        resp = await client.get(folders_url)
        assert 200 == resp.status_code
        assert 0 == len((await resp.get_json())["_items"])

        resp = await client.post(folders_url, json=folder)
        assert 201 == resp.status_code, await resp.get_data(as_text=True)
        parent_folder = await resp.get_json()
        assert "_id" in parent_folder

        resp = await client.get(folders_url)
        assert 200 == resp.status_code
        assert 1 == len((await resp.get_json())["_items"])

        folder["name"] = "test"
        folder["parent"] = parent_folder["_id"]
        resp = await client.post(folders_url, json=folder)
        assert 201 == resp.status_code, await resp.get_data(as_text=True)
        child_folder = await resp.get_json()

        topic = {
            "label": "Test",
            "query": "test",
            "topic_type": "wire",
            "folder": child_folder["_id"],
        }

        resp = await client.post(topics_url, json=topic)
        assert 201 == resp.status_code, await resp.get_data(as_text=True)

        resp = await client.patch(self_href(parent_folder), json={"name": "bar"}, headers=if_match(parent_folder))
        assert 200 == resp.status_code

        parent_folder.update(await resp.get_json())

        resp = await client.get(self_href(parent_folder))
        assert 200 == resp.status_code

        resp = await client.delete(self_href(parent_folder), headers=if_match(parent_folder))
        assert 204 == resp.status_code

        # deleting parent will delete children
        resp = await client.get(folders_url)
        assert 200 == resp.status_code
        assert 0 == len((await resp.get_json())["_items"]), "child folders should be deleted"

        # deleting folders will delete topics
        resp = await client.get(topics_url)
        assert 200 == resp.status_code
        assert 0 == len((await resp.get_json())["_items"]), "topics in folders should be deleted"


async def test_topic_folders_unique_validation(client):
    await utils.login(client, {"email": PUBLIC_USER_EMAIL})
    folder = {"name": "test", "section": "wire"}

    # create user topic
    resp = await client.post(user_topic_folders_url, json=folder)
    assert 201 == resp.status_code, await resp.get_data(as_text=True)

    # second one should raise DuplicateKeyError
    try:
        resp = await client.post(user_topic_folders_url, json=folder)
    except pymongo.errors.DuplicateKeyError:
        # assert that the DuplicateKeyError occurred as expected
        print("DuplicateKeyError for user topic folder as expected")
    else:
        # If no exception is raised, fail the test
        assert False, "Expected DuplicateKeyError for user topic folder, but got success"

    # create company topic with same name
    print("URL=")
    print(company_topic_folders_url)
    resp = await client.post(company_topic_folders_url, json=folder)
    assert 201 == resp.status_code, await resp.get_data(as_text=True)

    # second one should raise DuplicateKeyError for company topic
    try:
        resp = await client.post(company_topic_folders_url, json=folder)
    except pymongo.errors.DuplicateKeyError:
        # assert that the DuplicateKeyError occurred as expected
        print("DuplicateKeyError for company topic folder as expected")
    else:
        # If no exception is raised, fail the test
        assert False, "Expected DuplicateKeyError for company topic folder, but got success"

    # check case-insensitive uniqueness for user topic
    folder["name"] = "Test"
    try:
        resp = await client.post(user_topic_folders_url, json=folder)
    except pymongo.errors.DuplicateKeyError:
        print("DuplicateKeyError for case-insensitive user topic folder as expected")
    else:
        assert False, "Expected DuplicateKeyError for case-insensitive user topic folder, but got success"

    # check case-insensitive uniqueness for company topic
    try:
        resp = await client.post(company_topic_folders_url, json=folder)
    except pymongo.errors.DuplicateKeyError:
        print("DuplicateKeyError for case-insensitive company topic folder as expected")
    else:
        assert False, "Expected DuplicateKeyError for case-insensitive company topic folder, but got success"


async def test_topic_subscriber_auto_enable_user_emails(app, client, navigation_items):
    await utils.login_public(client)
    users_service = UsersService()
    user: UserResourceModel = await users_service.find_by_id(PUBLIC_USER_ID)
    topic = deepcopy(base_topic)

    # Make sure we start with user emails disabled
    await users_service.update(user.id, {"receive_email": False})
    user = await users_service.find_by_id(PUBLIC_USER_ID)
    assert user.receive_email is False

    # Create a new topic, with the current user as a subscriber
    topic["subscribers"] = [
        {
            "user_id": user.id,
            "notification_type": "real-time",
        }
    ]
    resp = await client.post(topics_url, json=topic)
    assert resp.status_code == 201, await resp.get_data(as_text=True)
    topic_id = (await resp.get_json())["_id"]
    topic = await TopicService().find_by_id(topic_id)
    topic = json.loads(topic.model_dump_json())

    # Make sure user emails are enabled after creating the topic
    user = await users_service.find_by_id(PUBLIC_USER_ID)
    assert user.receive_email is True

    # Disable the user emails again
    await users_service.update(user.id, {"receive_email": False})
    user = await users_service.find_by_id(PUBLIC_USER_ID)
    assert user.receive_email is False

    # Update the topic, this time removing the user as a subscriber
    topic["subscribers"] = []
    topic.pop("created")
    resp = await client.post(f"/topics/{topic_id}", json=topic)
    assert resp.status_code == 200, await resp.get_data(as_text=True)

    # Make sure user emails are still disabled
    user = await users_service.find_by_id(PUBLIC_USER_ID)
    assert user.receive_email is False

    # Update the topic, this time adding the user as a subscriber
    topic["subscribers"] = [
        {
            "user_id": user.id,
            "notification_type": "real-time",
        }
    ]
    resp = await client.post(f"/topics/{topic_id}", json=topic)
    assert resp.status_code == 200, await resp.get_data(as_text=True)

    # And make sure user emails are re-enabled again
    user = await users_service.find_by_id(PUBLIC_USER_ID)
    assert user.receive_email is True


async def test_remove_user_topics_on_user_delete(client, app):
    await create_entries_for(
        "topics",
        [
            {"_id": ObjectId(), "label": "test1", "user": PUBLIC_USER_ID, "is_global": False, "topic_type": "wire"},
            {
                "_id": ObjectId(),
                "label": "test2",
                "topic_type": "wire",
                "subscribers": [
                    {
                        "user_id": PUBLIC_USER_ID,
                        "notification_type": "real-time",
                    },
                    {
                        "user_id": TEST_USER_ID,
                        "notification_type": "real-time",
                    },
                ],
            },
            {
                "_id": ObjectId(),
                "label": "test3",
                "topic_type": "wire",
                "user": PUBLIC_USER_ID,
                "is_global": True,
                "subscribers": [
                    {
                        "user_id": PUBLIC_USER_ID,
                        "notification_type": "real-time",
                    },
                    {
                        "user_id": TEST_USER_ID,
                        "notification_type": "real-time",
                    },
                ],
            },
        ],
    )

    await create_entries_for(
        "user_topic_folders",
        [
            {"_id": ObjectId(), "name": "delete", "user": PUBLIC_USER_ID, "section": "wire"},
            {"_id": ObjectId(), "name": "skip", "user": TEST_USER_ID, "section": "wire"},
        ],
    )

    cursor = await TopicService().search(lookup={})
    topics = await cursor.to_list_raw()
    assert 3 == len(topics)

    cursor = await UserFoldersResourceService().search(lookup={})
    folders = await cursor.to_list_raw()
    assert 2 == len(folders)

    # TODO-ASYNC:- Test cases based on signal

    # await client.delete(f"/users/{PUBLIC_USER_ID}")

    # # make sure it's editable later
    # resp = await client.get(f"/api/users/{PUBLIC_USER_ID}/topics")
    # assert 200 == resp.status_code

    # cursor = await TopicService().search(lookup={})
    # topics = await cursor.to_list_raw()
    # assert 2 == len(topics)
    # assert "test2" == topics[0]["label"]
    # assert 1 == len(topics[0]["subscribers"])
    # assert "test3" == topics[1]["label"]
    # assert None is topics[1].get("user")

    # cursor = await UserFoldersResourceService().search(lookup={})
    # folders = await cursor.to_list_raw()
    # assert 1 == len(folders)
    # assert "skip" == folders[0]["name"]


async def test_created_field_in_topic_url(client):
    topic_payload = {
        "_id": ObjectId(),
        "label": "Foo",
        "query": "foo",
        "topic_type": "wire",
        "created": {"date_filter": "last_week"},
    }
    await utils.login(client, {"email": PUBLIC_USER_EMAIL})
    resp = await client.post(topics_url, json=deepcopy(topic_payload))
    assert 201 == resp.status_code
    resp = await client.get(topics_url)
    assert 200 == resp.status_code
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])
    topic = TopicResourceModel.from_dict(data["_items"][0])
    assert topic.label == "Foo"

    assert get_topic_url(topic) == "http://localhost:5050/wire?q=foo&created=%7B%22date_filter%22:+%22last_week%22%7D"

    resp = await client.post(
        "topics/{}".format(data["_items"][0]["_id"]),
        json={"label": "test123", "created": {"date_filter": "today"}},
    )
    assert 200 == resp.status_code

    resp = await client.get(topics_url)
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])
    topic = TopicResourceModel.from_dict(data["_items"][0])

    assert topic.label == "test123"
    assert get_topic_url(topic) == "http://localhost:5050/wire?created=%7B%22date_filter%22:+%22today%22%7D"
