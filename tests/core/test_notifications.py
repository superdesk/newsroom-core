import datetime

from quart import json
from bson import ObjectId
from pytest import fixture

from superdesk.utc import utcnow

from newsroom.notifications import get_user_notifications, NotificationsService
from ..fixtures import PUBLIC_USER_ID, TEST_USER_ID

TEST_ITEM_ID = ObjectId()
TEST_USER = str(PUBLIC_USER_ID)
TEST_NOTIFICATION = {"item": TEST_ITEM_ID, "user": TEST_USER, "resource": "test-resource", "action": "test-action"}
USER_NOTIFICATIONS_URL = f"users/{TEST_USER}/notifications"


@fixture
def service() -> NotificationsService:
    return NotificationsService()


async def test_notification_has_unique_id(service, app):
    app.config["NOTIFICATIONS_TTL"] = 1
    await service.create_or_update([TEST_NOTIFICATION])

    notifications = await get_user_notifications(PUBLIC_USER_ID)
    assert len(notifications) == 1
    assert notifications[0]["_id"] == f"{TEST_USER}_{TEST_ITEM_ID}"


async def test_notification_updates_with_unique_id(app, service):
    # first create base notification
    await service.create_or_update([TEST_NOTIFICATION])

    # update the existing notification with an older created date
    test_notification_id = f"{TEST_USER}_{TEST_ITEM_ID}"
    updates = dict(_created=utcnow() - datetime.timedelta(hours=1))
    await service.update(test_notification_id, updates)
    user_notifications = await get_user_notifications(PUBLIC_USER_ID)

    assert len(user_notifications) == 1
    assert user_notifications[0]["_id"] == f"{TEST_USER}_{TEST_ITEM_ID}"

    app.config["NOTIFICATIONS_TTL"] = 1
    old_created = user_notifications[0]["_created"]

    # now let's try create or update once more
    await service.create_or_update([TEST_NOTIFICATION])
    notifications = await get_user_notifications(PUBLIC_USER_ID)
    new_created = notifications[0]["_created"]

    # should still be only 1 notification but created should have been updated
    assert len(notifications) == 1
    assert old_created != new_created


async def test_delete_notification_fails_for_different_user(client, service):
    async with client.session_transaction() as session:
        session["user"] = TEST_USER

    test_notification_id = f"{TEST_USER}_{TEST_ITEM_ID}"
    await service.create_or_update([TEST_NOTIFICATION])

    async with client.session_transaction() as session:
        session["user"] = str(TEST_USER_ID)
        session["name"] = "tester"

    resp = await client.delete(f"/users/{TEST_USER}/notifications/{test_notification_id}")
    assert 403 == resp.status_code


async def test_delete_notification(client, service):
    await service.create_or_update([TEST_NOTIFICATION])

    async with client.session_transaction() as session:
        session["user"] = TEST_USER
        session["name"] = "tester"

    resp = await client.get(USER_NOTIFICATIONS_URL)
    data = json.loads(await resp.get_data())
    notify_id = data["notifications"][0]["_id"]

    resp = await client.delete(f"/users/{TEST_USER}/notifications/{notify_id}")
    assert 200 == resp.status_code

    resp = await client.get(USER_NOTIFICATIONS_URL)
    data = json.loads(await resp.get_data())
    assert 0 == len(data["notifications"])


async def test_delete_all_notifications(client, service):
    await service.create_or_update(
        [
            TEST_NOTIFICATION,
            {
                "item": ObjectId(),
                "user": TEST_USER,
                "resource": "test-resources",
                "action": "test-action",
                "created": utcnow() - datetime.timedelta(days=1),
            },
        ]
    )

    async with client.session_transaction() as session:
        session["user"] = TEST_USER
        session["name"] = "tester"

    resp = await client.get(USER_NOTIFICATIONS_URL)
    data = json.loads(await resp.get_data())
    assert 2 == len(data["notifications"])

    resp = await client.delete(f"/users/{TEST_USER}/notifications")
    assert 200 == resp.status_code

    resp = await client.get(USER_NOTIFICATIONS_URL)
    data = json.loads(await resp.get_data())
    assert 0 == len(data["notifications"])
