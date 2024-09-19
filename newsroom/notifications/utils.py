import datetime

from bson import ObjectId
import superdesk

from typing import Any
from superdesk.utc import utcnow
from superdesk.flask import session
from superdesk.core import get_app_config
from superdesk.notification import push_notification

from .services import NotificationsService


def user_notifications_lookup(user_id: str | ObjectId) -> dict[str, Any]:
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)

    ttl = get_app_config("NOTIFICATIONS_TTL", 1)
    return {
        "user": user_id,
        "_created": {"$gte": utcnow() - datetime.timedelta(days=ttl)},
    }


async def get_user_notifications(user_id: str) -> list[dict[str, Any]]:
    """
    Returns the notification entries for the given user
    """
    lookup = user_notifications_lookup(user_id)
    cursor = await NotificationsService().search(lookup)
    return await cursor.to_list_raw()


async def get_initial_notifications() -> dict[str, Any] | None:
    """
    Returns the stories that user has notifications for
    :return: List of stories. None if there is not user session.
    """
    if not session.get("user"):
        return None

    cursor = await NotificationsService().search(lookup=user_notifications_lookup(session["user"]))

    return {
        "user": str(session["user"]) if session["user"] else None,
        "notificationCount": await cursor.count(),
    }


async def get_notifications_with_items() -> dict[str, Any] | None:
    """
    Returns the stories that user has notifications for
    :return: List of stories. None if there is not user session.
    """
    if not session.get("user"):
        return None

    saved_notifications = await get_user_notifications(session["user"])
    item_ids = [n["item"] for n in saved_notifications]
    items = []

    try:
        items.extend(superdesk.get_resource_service("wire_search").get_items(item_ids))
    except (KeyError, TypeError):  # wire disabled
        pass
    try:
        items.extend(superdesk.get_resource_service("agenda").get_items(item_ids))
    except (KeyError, TypeError):  # agenda disabled
        pass
    try:
        items.extend(superdesk.get_resource_service("topics").get_items(item_ids))
    except (KeyError, TypeError):  # topics disabled
        pass

    return {
        "user": str(session["user"]) if session["user"] else None,
        "items": list(items),
        "notifications": saved_notifications,
    }


async def save_user_notifications(entries: list[dict[str, Any]]):
    """
    Saves the given notification entries and notify via push with the
    count of the saved notifications
    """
    service = NotificationsService()

    notification_ids = await service.create_or_update(entries)
    new_notifications = await service.find_items_by_ids(notification_ids)

    # iterate over the new notifications and collect the number
    # of new notifications per user
    notification_counts: dict[str, int] = {}

    for entry in new_notifications:
        user_id = str(entry.user)
        notification_counts.setdefault(user_id, 0)
        notification_counts[user_id] += 1

    # We only send the additional notification counts, and leave it up to the client
    # to request the list of notifications, when required
    push_notification("new_notifications", counts=notification_counts)
