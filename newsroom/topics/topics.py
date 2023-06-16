import newsroom
import superdesk

from bson import ObjectId
from newsroom.utils import set_original_creator, set_version_creator


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
            "schema": newsroom.Resource.rel("users", required=True),
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
    datasource = {"source": "topics", "default_sort": [("name", 1)]}


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
            updates["subscribers"] = [original["user"]] if original["user"] in original.get("subscribers", []) else []

        if updates.get("folder"):
            updates["folder"] = ObjectId(updates["folder"])

    def get_items(self, item_ids):
        return self.get(req=None, lookup={"_id": {"$in": item_ids}})


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


def get_topics_with_subscribers(topic_type: str):
    return list(
        superdesk.get_resource_service("topics").get(
            req=None,
            lookup={
                "$and": [
                    {"subscribers": {"$exists": True, "$ne": []}},
                    {"topic_type": topic_type},
                ]
            },
        )
    )


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


topics_service = TopicsService()
