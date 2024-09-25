from copy import deepcopy
from typing import Any

from bson import ObjectId
from superdesk.utc import utcnow
from superdesk.core.resources import AsyncResourceService

from .models import Notification, NotificationQueue, NotificationTopic


class NotificationsService(AsyncResourceService[Notification]):
    async def create_or_update(self, entries: list[dict[str, Any]]) -> list[str]:
        """
        Save the given notifications entries into the database. If the notification entry already
        exists in the database then it proceed to execute an update instead
        """
        from newsroom.users import UsersService

        now = utcnow()
        ids = []

        for doc in entries:
            user_id = doc["user"]
            user = await UsersService().find_by_id(user_id)

            if user is None or not user.receive_app_notifications:
                continue

            notification_id = f"{user_id}_{doc['item']}"
            original = await self.find_by_id(notification_id)

            if original:
                await self.update(
                    notification_id,
                    updates={
                        "_created": now,
                        "action": doc.get("action") or original.action,
                        "data": doc.get("data") or original.data,
                    },
                )
            else:
                creation_data = {
                    "_id": notification_id,
                    "user": ObjectId(doc["user"]),
                }
                doc.update(creation_data)
                await self.create([doc])

            ids.append(notification_id)

        return ids

    async def find_items_by_ids(self, item_ids: list[str]) -> list[Notification]:
        """
        Fetches and returns the notifications entries from database for the given list of IDs
        """
        cursor = await self.search({"_id": {"$in": item_ids}})
        return await cursor.to_list()


class NotificationQueueService(AsyncResourceService[NotificationQueue]):
    async def add_item_to_queue(self, user_id: ObjectId, section: str, topic_id: ObjectId, item: dict[str, Any]):
        """Add an item to the user's notification queue for a specific topic.

        If the queue or topic doesn't exist, create them. Then, append the item to the topic's item list.

        Args:
            user_id (ObjectId): The user's unique identifier.
            section (str): The section associated with the topic.
            topic_id (ObjectId): The topic's unique identifier.
            item (dict[str, Any]): The item to add, containing at least '_id' and 'versioncreated' keys.
        """
        original = await self.find_one(user=user_id)

        if not original:
            # Create a new schedule
            await self.create(
                [
                    {
                        "_id": ObjectId(),
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
            updates = {"topics": deepcopy(original.topics or [])}

            topic_queue = next((topic for topic in updates["topics"] if topic.topic_id == topic_id), None)

            if topic_queue is None:
                topic_queue = NotificationTopic(
                    topic_id=topic_id, section=section, last_item_arrived=item["versioncreated"]
                )
                updates["topics"].append(topic_queue)

            topic_queue.items.append(item["_id"])
            topic_queue.last_item_arrived = item["versioncreated"]

            await self.update(original.id, updates)

    async def reset_queue(self, user_id: ObjectId):
        """Delete all notification queue entries for a user.

        Args:
            user_id (ObjectId): The user's unique identifier.
        """
        await self.delete_many({"user": user_id})
