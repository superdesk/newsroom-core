from quart import json
from bson import ObjectId
import datetime
from superdesk.utc import utcnow
from superdesk import get_resource_service
from newsroom.notifications import get_user_notifications
from ..fixtures import init_company, PUBLIC_USER_ID, TEST_USER_ID  # noqa

user = str(PUBLIC_USER_ID)

notification = {"item": "Foo", "user": user}

notifications_url = "users/%s/notifications" % user


async def test_notification_has_unique_id(client, app):
    app.config["NOTIFICATIONS_TTL"] = 1
    get_resource_service("notifications").post([notification])
    notifications = get_user_notifications(ObjectId(user))
    assert len(notifications) == 1
    assert notifications[0]["_id"] == "{}_Foo".format(user)


async def test_notification_updates_with_unique_id(client, app):
    get_resource_service("notifications").post([notification])
    old_notifications = get_user_notifications(ObjectId(user))
    app.data.update(
        "notifications",
        "{}_Foo".format(user),
        {"created": utcnow() - datetime.timedelta(hours=1)},
        old_notifications[0],
    )
    old_notifications = get_user_notifications(ObjectId(user))
    app.config["NOTIFICATIONS_TTL"] = 1
    old_created = old_notifications[0]["created"]
    assert len(old_notifications) == 1
    assert old_notifications[0]["_id"] == "{}_Foo".format(user)
    get_resource_service("notifications").post([notification])
    notifications = get_user_notifications(ObjectId(user))
    new_created = notifications[0]["created"]
    assert len(notifications) == 1
    assert old_created != new_created


async def test_delete_notification_fails_for_different_user(client):
    async with client.session_transaction() as session:
        session["user"] = user

    get_resource_service("notifications").post([notification])
    id = "{}_Foo".format(user)

    async with client.session_transaction() as session:
        session["user"] = str(TEST_USER_ID)
        session["name"] = "tester"

    resp = await client.delete("/users/{}/notifications/{}".format(user, id))
    assert 403 == resp.status_code


async def test_delete_notification(client):
    get_resource_service("notifications").post([notification])

    async with client.session_transaction() as session:
        session["user"] = user
        session["name"] = "tester"

    resp = await client.get(notifications_url)
    data = json.loads(await resp.get_data())
    notify_id = data["notifications"][0]["_id"]

    resp = await client.delete("/users/{}/notifications/{}".format(user, notify_id))
    assert 200 == resp.status_code

    resp = await client.get(notifications_url)
    data = json.loads(await resp.get_data())
    assert 0 == len(data["notifications"])


async def test_delete_all_notifications(client):
    get_resource_service("notifications").post([notification, {"item": "Bar", "user": user}])

    async with client.session_transaction() as session:
        session["user"] = user
        session["name"] = "tester"

    resp = await client.get(notifications_url)
    data = json.loads(await resp.get_data())
    assert 2 == len(data["notifications"])

    resp = await client.delete("/users/{}/notifications".format(user))
    assert 200 == resp.status_code

    resp = await client.get(notifications_url)
    data = json.loads(await resp.get_data())
    assert 0 == len(data["notifications"])
