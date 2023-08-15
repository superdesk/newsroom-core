from copy import deepcopy

from newsroom import Resource, Service, MongoIndexes


class NotificationQueueResource(Resource):
    resource_methods = ["GET"]
    item_methods = ["GET", "PATCH", "DELETE"]
    internal_resource = True

    schema = {
        "user": Resource.rel("users"),
        "topics": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "items": {
                        "type": "list",
                        "schema": Resource.rel("items"),
                    },
                    "topic_id": Resource.rel("topics"),
                    "last_item_arrived": {"type": "datetime"},
                    "section": {"type": "string"},
                },
            },
        },
    }

    mongo_indexes: MongoIndexes = {
        "user_id": ([("user", 1)], {}),
    }


class NotificationQueueService(Service):
    def add_item_to_queue(self, user_id, section, topic_id, item):
        original = self.find_one(req=None, user=user_id)

        if not original:
            # Create a new schedule
            self.create(
                [
                    {
                        "user": user_id,
                        "topics": [
                            {
                                "items": [item["_id"]],
                                "topic_id": topic_id,
                                "section": section,
                                "last_item_arrived": item["versioncreated"],
                            }
                        ],
                    }
                ]
            )
        else:
            # Update an existing schedule
            updates = {"topics": deepcopy(original.get("topics") or [])}

            topic_queue = next((topic for topic in updates["topics"] if topic.get("topic_id") == topic_id), None)

            if topic_queue is None:
                topic_queue = {
                    "topic_id": topic_id,
                    "section": section,
                }
                updates["topics"].append(topic_queue)

            topic_queue.setdefault("items", []).append(item["_id"])
            topic_queue["last_item_arrived"] = item["versioncreated"]

            self.update(original["_id"], updates, original)

    def reset_queue(self, user_id):
        original = self.find_one(req=None, user=user_id)

        if not original:
            # No schedule found, no need to clear
            return

        self.update(original["_id"], {"topics": []}, original)
