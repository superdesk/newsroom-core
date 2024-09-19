import datetime

from bson import ObjectId

import superdesk
from superdesk.core import get_app_config
from superdesk.utc import utcnow
from superdesk.flask import session
import newsroom
from newsroom.topics.topics_async import TopicService


class NotificationsResource(newsroom.Resource):
    url = 'users/<regex("[a-f0-9]{24}"):user>/notifications'

    resource_methods = ["GET"]
    item_methods = ["GET", "PATCH", "DELETE"]

    schema = {
        "_id": {"type": "string", "unique": True},
        "item": newsroom.Resource.rel("items"),
        "user": newsroom.Resource.rel("users"),
        "created": {"type": "datetime", "nullable": True},
        "resource": {"type": "string"},
        "action": {"type": "string"},
        "data": {"type": "dict", "schema": {}, "allow_unknown": True},
    }

    datasource = {"default_sort": [("created", -1)]}

    mongo_indexes: newsroom.MongoIndexes = {
        "user_created": ([("user", 1), ("created", -1)], {}),
    }


class NotificationsService(newsroom.Service):
    def create(self, docs, **kwargs):
        now = utcnow()
        ids = []

        for doc in docs:
            user_id = str(doc["user"])
            user = superdesk.get_resource_service("users").find_one(req=None, _id=user_id)

            if not user.get("receive_app_notifications"):
                continue

            notification_id = "_".join(map(str, [user_id, doc["item"]]))
            original = self.find_one(req=None, _id=notification_id)

            if original:
                self.update(
                    id=notification_id,
                    updates={
                        "created": now,
                        "action": doc.get("action") or original.get("action"),
                        "data": doc.get("data") or original.get("data"),
                    },
                    original=original,
                )
            else:
                super().create(
                    [
                        {
                            "_id": notification_id,
                            "created": now,
                            "user": ObjectId(doc["user"]),
                            "item": doc["item"],
                            "resource": doc.get("resource"),
                            "action": doc.get("action"),
                            "data": doc.get("data"),
                        }
                    ]
                )

            ids.append(notification_id)

        return ids

    def get_items(self, item_ids):
        return self.get(req=None, lookup={"_id": {"$in": item_ids}})


def get_user_notifications(user_id):
    ttl = get_app_config("NOTIFICATIONS_TTL", 1)
    lookup = {
        "user": user_id,
        "created": {"$gte": utcnow() - datetime.timedelta(days=ttl)},
    }

    return list(superdesk.get_resource_service("notifications").get(req=None, lookup=lookup))


def get_initial_notifications():
    """
    Returns the stories that user has notifications for
    :return: List of stories
    """
    if not session.get("user"):
        return None

    saved_notifications = get_user_notifications(session["user"])

    return {
        "user": str(session["user"]) if session["user"] else None,
        "notificationCount": len(list(saved_notifications)),
    }


async def get_notifications_with_items():
    """
    Returns the stories that user has notifications for
    :return: List of stories
    """
    if not session.get("user"):
        return None

    saved_notifications = get_user_notifications(session["user"])
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
        mongo_cursor = await TopicService().search(lookup={"_id": {"$in": item_ids}})
        topics_items = await mongo_cursor.to_list_raw()
        items.extend(topics_items)
    except (KeyError, TypeError):  # topics disabled
        pass
    return {
        "user": str(session["user"]) if session["user"] else None,
        "items": list(items),
        "notifications": saved_notifications,
    }
