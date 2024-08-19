from quart import json
from unittest import mock
from copy import deepcopy

from newsroom.topics.views import get_topic_url
from newsroom.users.model import UserResourceModel
from newsroom.users.service import UsersService
from ..fixtures import (  # noqa: F401
    PUBLIC_USER_NAME,
    PUBLIC_USER_EMAIL,
    init_company,
    PUBLIC_USER_ID,
    TEST_USER_ID,
    COMPANY_1_ID,
)
from ..utils import mock_send_email, get_resource_by_id
from tests import utils

base_topic = {
    "label": "Foo",
    "query": "foo",
    "notifications": False,
    "topic_type": "wire",
    "navigation": ["xyz"],
}

agenda_topic = {
    "label": "Foo",
    "query": "foo",
    "notifications": False,
    "topic_type": "agenda",
    "navigation": ["abc"],
}

user_id = str(PUBLIC_USER_ID)
test_user_id = str(TEST_USER_ID)
topics_url = "users/%s/topics" % user_id

user_topic_folders_url = "/api/users/{}/topic_folders".format(TEST_USER_ID)
company_topic_folders_url = "/api/companies/{}/topic_folders".format(COMPANY_1_ID)


async def test_topics_no_session(app):
    async with app.test_client() as client:
        resp = await client.get(topics_url)
        assert 302 == resp.status_code
        resp = await client.post(topics_url, data=deepcopy(base_topic))
        assert 302 == resp.status_code


async def test_post_topic_user(client):
    await utils.login(client, {"email": PUBLIC_USER_EMAIL})
    resp = await client.post(topics_url, json=deepcopy(base_topic))
    assert 201 == resp.status_code
    resp = await client.get(topics_url)
    assert 200 == resp.status_code
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])


async def test_update_topic_fails_for_different_user(app):
    async with app.test_client() as client:
        await utils.login(client, {"email": PUBLIC_USER_EMAIL})
        resp = await client.post(topics_url, json=deepcopy(base_topic))
        assert 201 == resp.status_code

        resp = await client.get(topics_url)
        data = json.loads(await resp.get_data())
        _id = data["_items"][0]["_id"]

    async with app.test_client() as client:
        await utils.login(client, {"email": "test@bar.com"})
        resp = await client.post("topics/{}".format(_id), json={"label": "test123"})
        assert 403 == resp.status_code


async def test_update_topic(client):
    await utils.login(client, {"email": PUBLIC_USER_EMAIL})
    resp = await client.post(topics_url, json=deepcopy(base_topic))
    assert 201 == resp.status_code

    resp = await client.get(topics_url)
    data = json.loads(await resp.get_data())
    _id = data["_items"][0]["_id"]

    resp = await client.post(
        "topics/{}".format(_id),
        json={"label": "test123"},
    )
    assert 200 == resp.status_code

    resp = await client.get(topics_url)
    data = json.loads(await resp.get_data())
    assert "test123" == data["_items"][0]["label"]


async def test_delete_topic(client):
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
async def test_share_wire_topics(client, app):
    topic = deepcopy(base_topic)
    topic_ids = app.data.insert("topics", [topic])
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

        assert resp.status_code == 201, resp.get_data().decode("utf-8")
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
async def test_share_agenda_topics(client, app):
    topic_ids = app.data.insert("topics", [agenda_topic])
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

        assert resp.status_code == 201, resp.get_data().decode("utf-8")
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
    topic = {"topic_type": "wire", "query": "art exhibition"}
    assert get_topic_url(topic) == "http://localhost:5050/wire?q=art+exhibition"

    topic = {"topic_type": "wire", "filter": {"location": [["Sydney"]]}}
    assert get_topic_url(topic) == "http://localhost:5050/wire?filter=%7B%22location%22:+%5B%5B%22Sydney%22%5D%5D%7D"

    topic = {"topic_type": "wire", "navigation": ["123"]}
    assert get_topic_url(topic) == "http://localhost:5050/wire?navigation=%5B%22123%22%5D"

    topic = {"topic_type": "wire", "navigation": ["123", "456"]}
    assert get_topic_url(topic) == "http://localhost:5050/wire?navigation=%5B%22123%22,+%22456%22%5D"

    topic = {"topic_type": "wire", "created": {"from": "2018-06-01"}}
    assert get_topic_url(topic) == "http://localhost:5050/wire?created=%7B%22from%22:+%222018-06-01%22%7D"

    topic = {"topic_type": "wire", "advanced": {"all": "Weather Sydney", "fields": ["headline", "body_html"]}}
    assert get_topic_url(topic) == (
        "http://localhost:5050/wire?advanced="
        "%7B%22all%22:+%22Weather+Sydney%22,+%22fields%22:+%5B%22headline%22,+%22body_html%22%5D%7D"
    )

    topic = {
        "topic_type": "wire",
        "query": "art exhibition",
        "filter": {"urgency": [3]},
        "navigation": ["123"],
        "created": {"from": "2018-06-01"},
        "advanced": {"all": "Weather Sydney", "fields": ["headline", "body_html"]},
    }
    assert (
        get_topic_url(topic) == "http://localhost:5050/wire?"
        "q=art+exhibition"
        "&filter=%7B%22urgency%22:+%5B3%5D%7D"
        "&navigation=%5B%22123%22%5D"
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

    # second one fails
    resp = await client.post(user_topic_folders_url, json=folder)
    assert 409 == resp.status_code, await resp.get_data(as_text=True)

    # create company topic with same name
    resp = await client.post(company_topic_folders_url, json=folder)
    assert 201 == resp.status_code, await resp.get_data(as_text=True)

    # second fails
    resp = await client.post(company_topic_folders_url, json=folder)
    assert 409 == resp.status_code, await resp.get_data(as_text=True)

    # check is case insensitive
    folder["name"] = "Test"
    resp = await client.post(user_topic_folders_url, json=folder)
    assert 409 == resp.status_code, await resp.get_data(as_text=True)

    # for both
    resp = await client.post(company_topic_folders_url, json=folder)
    assert 409 == resp.status_code, await resp.get_data(as_text=True)


async def test_topic_subscriber_auto_enable_user_emails(app, client):
    await utils.login(client, {"email": PUBLIC_USER_EMAIL})
    user: UserResourceModel = await UsersService().find_by_id(PUBLIC_USER_ID)
    user = json.loads(user.model_dump_json())
    topic = deepcopy(base_topic)

    async def disable_user_emails():
        user["receive_email"] = False
        resp = await client.post(f"/users/{PUBLIC_USER_ID}", form=user)
        assert resp.status_code == 200, await resp.get_data(as_text=True)

    # Make sure we start with user emails disabled
    await disable_user_emails()
    user = get_resource_by_id("users", PUBLIC_USER_ID)
    assert user["receive_email"] is False

    # Create a new topic, with the current user as a subscriber
    topic["subscribers"] = [
        {
            "user_id": user["_id"],
            "notification_type": "real-time",
        }
    ]
    resp = await client.post(topics_url, json=topic)
    assert resp.status_code == 201, await resp.get_data(as_text=True)
    topic_id = (await resp.get_json())["_id"]
    topic = get_resource_by_id("topics", topic_id)

    # Make sure user emails are enabled after creating the topic
    user = get_resource_by_id("users", PUBLIC_USER_ID)
    assert user["receive_email"] is True

    # Disable the user emails again
    await disable_user_emails()
    user = get_resource_by_id("users", PUBLIC_USER_ID)
    assert user["receive_email"] is False

    # Update the topic, this time removing the user as a subscriber
    topic["subscribers"] = []
    resp = await client.post(f"/topics/{topic_id}", json=topic)
    assert resp.status_code == 200, await resp.get_data(as_text=True)

    # Make sure user emails are still disabled
    user = get_resource_by_id("users", PUBLIC_USER_ID)
    assert user["receive_email"] is False

    # Update the topic, this time adding the user as a subscriber
    topic["subscribers"] = [
        {
            "user_id": user["_id"],
            "notification_type": "real-time",
        }
    ]
    resp = await client.post(f"/topics/{topic_id}", json=topic)
    assert resp.status_code == 200, await resp.get_data(as_text=True)

    # And make sure user emails are re-enabled again
    user = get_resource_by_id("users", PUBLIC_USER_ID)
    assert user["receive_email"] is True


async def test_remove_user_topics_on_user_delete(client, app):
    app.data.insert(
        "topics",
        [
            {
                "label": "test1",
                "user": PUBLIC_USER_ID,
                "is_global": False,
            },
            {
                "label": "test2",
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
                "label": "test3",
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

    app.data.insert(
        "user_topic_folders",
        [
            {"name": "delete", "user": PUBLIC_USER_ID},
            {"name": "skip", "user": TEST_USER_ID},
        ],
    )

    topics, _ = app.data.find("topics", req=None, lookup=None)
    assert 3 == topics.count()

    folders, _ = app.data.find("user_topic_folders", req=None, lookup=None)
    assert 2 == folders.count()

    await client.delete(f"/users/{PUBLIC_USER_ID}")

    # make sure it's editable later
    resp = await client.get(f"/api/users/{PUBLIC_USER_ID}/topics")
    assert 200 == resp.status_code

    topics, _ = app.data.find("topics", req=None, lookup=None)
    assert 2 == topics.count()
    assert "test2" == topics[0]["label"]
    assert 1 == len(topics[0]["subscribers"])
    assert "test3" == topics[1]["label"]
    assert None is topics[1].get("user")

    folders, _ = app.data.find("user_topic_folders", req=None, lookup=None)
    assert 1 == folders.count()
    assert "skip" == folders[0]["name"]
