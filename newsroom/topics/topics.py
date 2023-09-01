from typing import Optional, List, Dict, Any
import enum

import newsroom
import superdesk

from bson import ObjectId
from newsroom.types import Topic, User
from newsroom.utils import set_original_creator, set_version_creator


class TopicNotificationType(enum.Enum):
    # NONE = "none"
    REAL_TIME = "real-time"
    SCHEDULED = "scheduled"


class TopicsResource(newsroom.Resource):
    url = 'users/<regex("[a-f0-9]{24}"):user>/topics'
    resource_methods = ["GET", "POST"]
    item_methods = ["GET", "PATCH", "DELETE"]
    collation = True
    schema = {
        "label": {"type": "string", "required": True},
        "query": {"type": "string", "nullable": True},
        "filter": {"type": "dict", "nullable": True},
        "created": {"type": "dict", "nullable": True},
        "user": newsroom.Resource.rel("users", required=True),  # This is the owner of the "My Topic"
        "company": newsroom.Resource.rel("companies", required=True),
        "is_global": {"type": "boolean", "default": False},
        "subscribers": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "user_id": newsroom.Resource.rel("users", required=True),
                    "notification_type": {
                        "type": "string",
                        "required": True,
                        "default": TopicNotificationType.REAL_TIME.value,
                        "allowed": [notify_type.value for notify_type in TopicNotificationType],
                    },
                },
            },
        },
        "timezone_offset": {"type": "integer", "nullable": True},
        "topic_type": {
            "type": "string",
            "required": True,
            "allowed": ["wire", "agenda"],
        },
        "navigation": {
            "type": "list",
            "nullable": True,
            "schema": {"type": "string"},
        },
        "original_creator": newsroom.Resource.rel("users"),
        "version_creator": newsroom.Resource.rel("users"),
        "folder": newsroom.Resource.rel("topic_folders", nullable=True),
        "advanced": {"type": "dict", "nullable": True},
    }
    datasource = {"source": "topics", "default_sort": [("label", 1)]}


class TopicsService(newsroom.Service):
    def on_create(self, docs):
        super().on_create(docs)
        for doc in docs:
            set_original_creator(doc)
            set_version_creator(doc)
            if doc.get("folder"):
                doc["folder"] = ObjectId(doc["folder"])

    def on_update(self, updates, original):
        super().on_update(updates, original)
        set_version_creator(updates)

        # If ``is_global`` has been turned off, then remove all subscribers
        # except for the owner of the Topic
        if original.get("is_global") and "is_global" in updates and not updates.get("is_global"):
            # First find the subscriber entry for the original user
            subscriber = next(
                (
                    subscriber
                    for subscriber in original.get("subscribers", [])
                    if subscriber["user_id"] == original["user"]
                ),
                None,
            )

            # Then construct new array with either subscriber found or empty list
            updates["subscribers"] = [subscriber] if subscriber is not None else []

        if updates.get("folder"):
            updates["folder"] = ObjectId(updates["folder"])

    def get_items(self, item_ids):
        return self.get(req=None, lookup={"_id": {"$in": item_ids}})

    def on_delete(self, doc):
        super().on_delete(doc)
        # remove topic from users personal dashboards
        users = superdesk.get_resource_service("users").get(req=None, lookup={"dashboards.topic_ids": doc["_id"]})
        for user in users:
            updates = {"dashboards": user["dashboards"].copy()}
            for dashboard in updates["dashboards"]:
                dashboard["topic_ids"] = [topic_id for topic_id in dashboard["topic_ids"] if topic_id != doc["_id"]]
            superdesk.get_resource_service("users").system_update(user["_id"], updates, user)


def get_user_topics(user_id):
    user = superdesk.get_resource_service("users").find_one(req=None, _id=ObjectId(user_id))
    return list(
        superdesk.get_resource_service("topics").get(
            req=None,
            lookup={
                "$or": [
                    {"user": user["_id"]},
                    {"$and": [{"company": user.get("company")}, {"is_global": True}]},
                ]
            },
        )
    )


def get_topics_with_subscribers(topic_type: Optional[str] = None) -> List[Topic]:
    lookup: Dict[str, Any] = (
        {"subscribers": {"$exists": True, "$ne": []}}
        if topic_type is None
        else {
            "$and": [
                {"subscribers": {"$exists": True, "$ne": []}},
                {"topic_type": topic_type},
            ]
        }
    )

    return list(
        superdesk.get_resource_service("topics").get(
            req=None,
            lookup=lookup,
        )
    )


def get_user_id_to_topic_for_subscribers(
    notification_type: Optional[str] = None,
) -> Dict[ObjectId, Dict[ObjectId, Topic]]:
    user_topic_map: Dict[ObjectId, Dict[ObjectId, Topic]] = {}
    for topic in get_topics_with_subscribers():
        for subscriber in topic.get("subscribers") or []:
            if notification_type is not None and subscriber["notification_type"] != notification_type:
                continue
            user_topic_map.setdefault(subscriber["user_id"], {})
            user_topic_map[subscriber["user_id"]][topic["_id"]] = topic

    return user_topic_map


def get_agenda_notification_topics_for_query_by_id(item, users):
    """
    Returns active topics for a given agenda item
    :param item: agenda item
    :param users: active users dict
    :return: list of topics
    """
    lookup = {
        "$and": [
            {"subscribers": {"$exists": True, "$ne": []}},
            {"topic_type": "agenda"},
            {"query": item["_id"]},
        ]
    }
    topics = list(superdesk.get_resource_service("topics").get(req=None, lookup=lookup))

    # filter out the topics those belong to inactive users
    return [t for t in topics if users.get(str(t["user"]))]


def auto_enable_user_emails(updates: Topic, original: Topic, user: User):
    if not updates.get("subscribers"):
        return

    # If current user is already subscribed to this topic,
    # then no need to enable their email notifications
    for subscriber in original.get("subscribers") or []:
        if subscriber["user_id"] == user["_id"]:
            return

    user_newly_subscribed = False
    for subscriber in updates.get("subscribers") or []:
        if subscriber["user_id"] == user["_id"]:
            user_newly_subscribed = True

    if not user_newly_subscribed:
        return

    # The current user subscribed to this topic in this update
    # Enable their email notifications now
    superdesk.get_resource_service("users").patch(user["_id"], updates={"receive_email": True})


topics_service = TopicsService()
