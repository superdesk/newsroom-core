from flask import json
from unittest import mock
from pytest import fixture
from copy import deepcopy
from newsroom.auth.utils import start_user_session

from newsroom.topics.views import get_topic_url
from ..fixtures import (  # noqa: F401
    PUBLIC_USER_NAME,
    init_company,
    PUBLIC_USER_ID,
    TEST_USER_ID,
    COMPANY_1_ID,
)
from ..utils import mock_send_email, get_resource_by_id

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


@fixture
def auth_client(client, public_user):
    with client as cli:
        with client.session_transaction() as session:
            start_user_session(public_user, session=session)
        yield cli


def test_topics_no_session(client, anonymous_user):
    resp = client.get(topics_url)
    assert 302 == resp.status_code
    resp = client.post(topics_url, data=deepcopy(base_topic))
    assert 302 == resp.status_code


def test_post_topic_user(client):
    with client as cli:
        with client.session_transaction() as session:
            session["user"] = user_id
            session["name"] = PUBLIC_USER_NAME
        resp = cli.post(topics_url, json=deepcopy(base_topic))
        assert 201 == resp.status_code
        resp = cli.get(topics_url)
        assert 200 == resp.status_code
        data = json.loads(resp.get_data())
        assert 1 == len(data["_items"])


def test_update_topic_fails_for_different_user(client):
    with client as app:
        with client.session_transaction() as session:
            session["user"] = user_id
            session["name"] = PUBLIC_USER_NAME
        resp = app.post(topics_url, json=deepcopy(base_topic))
        assert 201 == resp.status_code

        resp = app.get(topics_url)
        data = json.loads(resp.get_data())
        _id = data["_items"][0]["_id"]

        with client.session_transaction() as session:
            session["name"] = test_user_id
            session["user"] = test_user_id
        resp = app.post("topics/{}".format(_id), json={"label": "test123"})
        assert 403 == resp.status_code


def test_update_topic(client):
    with client as app:
        with client.session_transaction() as session:
            session["user"] = user_id
            session["name"] = PUBLIC_USER_NAME
        resp = app.post(topics_url, json=deepcopy(base_topic))
        assert 201 == resp.status_code

        resp = app.get(topics_url)
        data = json.loads(resp.get_data())
        _id = data["_items"][0]["_id"]

        resp = app.post(
            "topics/{}".format(_id),
            data=json.dumps({"label": "test123"}),
            content_type="application/json",
        )
        assert 200 == resp.status_code

        resp = app.get(topics_url)
        data = json.loads(resp.get_data())
        assert "test123" == data["_items"][0]["label"]


def test_delete_topic(client):
    with client as app:
        with client.session_transaction() as session:
            session["user"] = user_id
            session["name"] = PUBLIC_USER_NAME
        resp = app.post(topics_url, json=deepcopy(base_topic), content_type="application/json")
        assert 201 == resp.status_code

        resp = app.get(topics_url)
        data = json.loads(resp.get_data())
        _id = data["_items"][0]["_id"]

        resp = app.delete("topics/{}".format(_id))
        assert 200 == resp.status_code

        resp = app.get(topics_url)
        data = json.loads(resp.get_data())
        assert 0 == len(data["_items"])


@mock.patch("newsroom.email.send_email", mock_send_email)
def test_share_wire_topics(client, app):
    topic = deepcopy(base_topic)
    topic_ids = app.data.insert("topics", [topic])
    topic["_id"] = topic_ids[0]

    with app.mail.record_messages() as outbox:
        with client.session_transaction() as session:
            session["user"] = user_id
            session["name"] = "tester"
        resp = client.post(
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
def test_share_agenda_topics(client, app):
    topic_ids = app.data.insert("topics", [agenda_topic])
    agenda_topic["_id"] = topic_ids[0]

    with app.mail.record_messages() as outbox:
        with client.session_transaction() as session:
            session["user"] = user_id
            session["name"] = "tester"
        resp = client.post(
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


def test_get_topic_share_url(app):
    topic = {"topic_type": "wire", "query": "art exhibition"}
    assert get_topic_url(topic) == "http://localhost:5050/wire?q=art+exhibition"

    topic = {"topic_type": "wire", "filter": {"location": [["Sydney"]]}}
    assert get_topic_url(topic) == "http://localhost:5050/wire?filter=%7B%22location%22%3A+%5B%5B%22Sydney%22%5D%5D%7D"

    topic = {"topic_type": "wire", "navigation": ["123"]}
    assert get_topic_url(topic) == "http://localhost:5050/wire?navigation=%5B%22123%22%5D"

    topic = {"topic_type": "wire", "navigation": ["123", "456"]}
    assert get_topic_url(topic) == "http://localhost:5050/wire?navigation=%5B%22123%22%2C+%22456%22%5D"

    topic = {"topic_type": "wire", "created": {"from": "2018-06-01"}}
    assert get_topic_url(topic) == "http://localhost:5050/wire?created=%7B%22from%22%3A+%222018-06-01%22%7D"

    topic = {"topic_type": "wire", "advanced": {"all": "Weather Sydney", "fields": ["headline", "body_html"]}}
    assert get_topic_url(topic) == (
        "http://localhost:5050/wire?advanced="
        "%7B%22all%22%3A+%22Weather+Sydney%22%2C+%22fields%22%3A+%5B%22headline%22%2C+%22body_html%22%5D%7D"
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
        "&filter=%7B%22urgency%22%3A+%5B3%5D%7D"
        "&navigation=%5B%22123%22%5D"
        "&created=%7B%22from%22%3A+%222018-06-01%22%7D"
        "&advanced=%7B%22all%22%3A+%22Weather+Sydney%22%2C+%22fields%22%3A+%5B%22headline%22%2C+%22body_html%22%5D%7D"
    )


def self_href(doc):
    return "api/{}".format(doc["_links"]["self"]["href"])


def if_match(doc):
    return {"if-match": doc["_etag"]}


def test_topic_folders_crud(auth_client):
    urls = (user_topic_folders_url, company_topic_folders_url)
    for folders_url in urls:
        folder = {"name": "test", "section": "wire"}

        resp = auth_client.get(folders_url)
        assert 200 == resp.status_code
        assert 0 == len(resp.json["_items"])

        resp = auth_client.post(folders_url, json=folder)
        assert 201 == resp.status_code, resp.data.decode()
        parent_folder = resp.json
        assert "_id" in parent_folder

        resp = auth_client.get(folders_url)
        assert 200 == resp.status_code
        assert 1 == len(resp.json["_items"])

        folder["name"] = "test"
        folder["parent"] = parent_folder["_id"]
        resp = auth_client.post(folders_url, json=folder)
        assert 201 == resp.status_code, resp.data.decode()
        child_folder = resp.json

        topic = {
            "label": "Test",
            "query": "test",
            "topic_type": "wire",
            "folder": child_folder["_id"],
        }

        resp = auth_client.post(topics_url, json=topic)
        assert 201 == resp.status_code, resp.data.decode()

        resp = auth_client.patch(self_href(parent_folder), json={"name": "bar"}, headers=if_match(parent_folder))
        assert 200 == resp.status_code

        parent_folder.update(resp.json)

        resp = auth_client.get(self_href(parent_folder))
        assert 200 == resp.status_code

        resp = auth_client.delete(self_href(parent_folder), headers=if_match(parent_folder))
        assert 204 == resp.status_code

        # deleting parent will delete children
        resp = auth_client.get(folders_url)
        assert 200 == resp.status_code
        assert 0 == len(resp.json["_items"]), "child folders should be deleted"

        # deleting folders will delete topics
        resp = auth_client.get(topics_url)
        assert 200 == resp.status_code
        assert 0 == len(resp.json["_items"]), "topics in folders should be deleted"


def test_topic_folders_unique_validation(auth_client):
    folder = {"name": "test", "section": "wire"}

    # create user topic
    resp = auth_client.post(user_topic_folders_url, json=folder)
    assert 201 == resp.status_code, resp.data.decode()

    # second one fails
    resp = auth_client.post(user_topic_folders_url, json=folder)
    assert 409 == resp.status_code, resp.data.decode()

    # create company topic with same name
    resp = auth_client.post(company_topic_folders_url, json=folder)
    assert 201 == resp.status_code, resp.data.decode()

    # second fails
    resp = auth_client.post(company_topic_folders_url, json=folder)
    assert 409 == resp.status_code, resp.data.decode()

    # check is case insensitive
    folder["name"] = "Test"
    resp = auth_client.post(user_topic_folders_url, json=folder)
    assert 409 == resp.status_code, resp.data.decode()

    # for both
    resp = auth_client.post(company_topic_folders_url, json=folder)
    assert 409 == resp.status_code, resp.data.decode()


def test_topic_subscriber_auto_enable_user_emails(app, auth_client):
    user = get_resource_by_id("users", PUBLIC_USER_ID)
    topic = deepcopy(base_topic)

    def disable_user_emails():
        user["receive_email"] = False
        resp = auth_client.post(f"/users/{PUBLIC_USER_ID}", data=user)
        assert resp.status_code == 200, resp.get_data(as_text=True)

    # Make sure we start with user emails disabled
    disable_user_emails()
    user = get_resource_by_id("users", PUBLIC_USER_ID)
    assert user["receive_email"] is False

    # Create a new topic, with the current user as a subscriber
    topic["subscribers"] = [
        {
            "user_id": user["_id"],
            "notification_type": "real-time",
        }
    ]
    resp = auth_client.post(topics_url, json=topic)
    assert resp.status_code == 201, resp.get_data(as_text=True)
    topic_id = resp.get_json()["_id"]
    topic = get_resource_by_id("topics", topic_id)

    # Make sure user emails are enabled after creating the topic
    user = get_resource_by_id("users", PUBLIC_USER_ID)
    assert user["receive_email"] is True

    # Disable the user emails again
    disable_user_emails()
    user = get_resource_by_id("users", PUBLIC_USER_ID)
    assert user["receive_email"] is False

    # Update the topic, this time removing the user as a subscriber
    topic["subscribers"] = []
    resp = auth_client.post(f"/topics/{topic_id}", json=topic)
    assert resp.status_code == 200, resp.get_data(as_text=True)

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
    resp = auth_client.post(f"/topics/{topic_id}", json=topic)
    assert resp.status_code == 200, resp.get_data(as_text=True)

    # And make sure user emails are re-enabled again
    user = get_resource_by_id("users", PUBLIC_USER_ID)
    assert user["receive_email"] is True
