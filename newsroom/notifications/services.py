from typing import Any

from bson import ObjectId
from superdesk.utc import utcnow
from superdesk.core.resources import AsyncResourceService

from .model import Notification


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
                    "item": doc["item"],
                    "resource": doc.get("resource"),
                    "action": doc.get("action"),
                    "data": doc.get("data"),
                }
                await self.create([creation_data])

            ids.append(notification_id)

        return ids

    async def find_items_by_ids(self, item_ids: list[str]) -> list[Notification]:
        """
        Fetches and returns the notifications entries from database for the given list of IDs
        """
        cursor = await self.search({"_id": {"$in": item_ids}})
        return await cursor.to_list()
