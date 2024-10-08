import logging

from typing import Any, Set
from bson import ObjectId

from newsroom.types import Company, Topic, User
from newsroom.users.service import UsersService
from superdesk import get_resource_service
from superdesk.core import get_app_config

from newsroom.core import get_current_wsgi_app
from newsroom.history import get_history_users
from newsroom.utils import get_company_dict, get_user_dict
from newsroom.agenda.utils import push_agenda_item_notification
from newsroom.email import (
    send_new_item_notification_email,
    send_history_match_notification_email,
    send_item_killed_notification_email,
)
from newsroom.topics import get_agenda_notification_topics_for_query_by_id, get_topics_with_subscribers
from newsroom.notifications import push_notification, save_user_notifications, NotificationQueueService


logger = logging.getLogger(__name__)


# TODO-ASYNC: revisit when agenda and wire_search are async


def is_canceled(item: dict[str, Any]) -> bool:
    return item.get("pubstatus", item.get("state")) in ["canceled", "cancelled"]


class NotificationManager:
    async def notify_new_item(self, item: dict[str, Any], check_topics: bool = True):
        if not item or item.get("type") == "composite":
            return

        item_type = item.get("type")
        users_with_realtime_subscription: Set[ObjectId] = set()
        try:
            user_dict = await get_user_dict()
            user_ids = [u["_id"] for u in user_dict.values()]

            company_dict = await get_company_dict()
            company_ids = [c["_id"] for c in company_dict.values()]

            if item_type == "agenda":
                await push_agenda_item_notification("new_item", item=item)
            else:
                push_notification("new_item", _items=[item])

            if check_topics:
                if item_type == "text":
                    users_with_realtime_subscription = await self.notify_wire_topic_matches(
                        item, user_dict, company_dict
                    )
                else:
                    users_with_realtime_subscription = await self.notify_agenda_topic_matches(
                        item, user_dict, company_dict
                    )

            if get_app_config("NOTIFY_MATCHING_USERS") == "never":
                return

            if get_app_config("NOTIFY_MATCHING_USERS") == "cancel" and not is_canceled(item):
                return

            await self.notify_user_matches(
                item,
                user_dict,
                company_dict,
                user_ids,
                company_ids,
                users_with_realtime_subscription if not is_canceled(item) else set(),
            )
        except Exception as e:
            logger.exception(e)
            logger.error(f"Failed to notify users for new {item_type} item", extra={"_id": item["_id"]})

    async def notify_wire_topic_matches(
        self, item: dict[str, Any], users_dict: dict[str, User], companies_dict: dict[str, Company]
    ) -> Set[ObjectId]:
        topics = await get_topics_with_subscribers("wire")
        topic_matches = get_resource_service("wire_search").get_matching_topics(
            item["_id"], topics, users_dict, companies_dict
        )

        if not topic_matches:
            return set()

        push_notification("topic_matches", item=item, topics=topic_matches)
        return await self.send_topic_notification_emails(item, topics, topic_matches, users_dict, companies_dict)

    async def send_topic_notification_emails(
        self,
        item: dict[str, Any],
        topics: list[Topic],
        topic_matches: list,
        users: dict[str, User],
        companies: dict[str, Company],
    ) -> Set[ObjectId]:
        users_processed: Set[ObjectId] = set()
        users_with_realtime_subscription: Set[ObjectId] = set()
        notification_queue_service = NotificationQueueService()

        for topic in topics:
            if topic["_id"] not in topic_matches:
                continue

            for subscriber in topic.get("subscribers") or []:
                user = users.get(str(subscriber["user_id"]))

                if not user:
                    continue

                company = companies.get(str(user.get("company")))

                section = topic.get("topic_type") or "wire"
                if user["_id"] not in users_processed:
                    # Only send websocket notification once for each item
                    await save_user_notifications(
                        [
                            dict(
                                user=user["_id"],
                                item=item["_id"],
                                resource=section,
                                action="topic_matches",
                                data=None,
                            )
                        ]
                    )
                    users_processed.add(user["_id"])

                if not user.get("receive_email"):
                    continue
                elif subscriber.get("notification_type") == "scheduled":
                    await notification_queue_service.add_item_to_queue(user["_id"], section, topic["_id"], item)
                elif user["_id"] in users_with_realtime_subscription:
                    # This user has already received a realtime notification email about this item
                    # No need to send another
                    continue
                else:
                    users_with_realtime_subscription.add(user["_id"])
                    search_service = get_resource_service("wire_search" if topic["topic_type"] == "wire" else "agenda")
                    query = search_service.get_topic_query(
                        topic, user, company, args={"es_highlight": 1, "ids": [item["_id"]]}
                    )

                    items = list(search_service.get_items_by_query(query, size=1))
                    highlighted_item = item

                    if len(items) > 0:
                        highlighted_item = items[0]

                    await send_new_item_notification_email(
                        user,
                        topic["label"],
                        item=highlighted_item,
                        section=section,
                    )

        return users_with_realtime_subscription

    async def notify_user_matches(
        self,
        item: dict[str, Any],
        users_dict: dict[str, Any],
        companies_dict: dict[str, Company],
        user_ids: list[ObjectId],
        company_ids: list[ObjectId],
        users_with_realtime_subscription: set[ObjectId],
    ):
        """Send notification to users who have downloaded or bookmarked the provided item"""

        related_items = item.get("ancestors", [])
        related_items.append(item["_id"])
        is_text = item.get("type") == "text"

        users_processed = []
        users_with_paused_notifications = set(
            [user["_id"] for user in users_dict.values() if UsersService.user_has_paused_notifications(user)]
        )

        def _get_users(section):
            """Get the list of users who have downloaded or bookmarked the items"""
            # Get users who have downloaded any of the items
            user_list = get_history_users(related_items, user_ids, company_ids, section, "download")

            if is_text and section != "agenda":
                # Add users who have bookmarked any of the items
                service = get_resource_service("{}_search".format(section))
                bookmarked_users = service.get_matching_bookmarks(related_items, users_dict, companies_dict)

                user_list.extend(bookmarked_users)

            # Add users if this section is wire
            # Or if the user is not already in the list of users for wire
            user_list = [
                user_id
                for user_id in user_list
                if user_id not in users_processed
                and ObjectId(user_id) not in users_with_realtime_subscription
                and ObjectId(user_id) not in users_with_paused_notifications
            ]

            users_processed.extend(user_list)

            # Remove duplicates and return the list
            return list(set(user_list))

        async def _send_notification(section, users_ids):
            if not users_ids:
                return

            await save_user_notifications(
                [
                    dict(
                        user=user,
                        item=item["_id"],
                        resource=item.get("type"),
                        action="history_match",
                        data=None,
                    )
                    for user in users_ids
                ]
            )

            await self.send_user_notification_emails(item, users_ids, users_dict, section)

        # First add users for the 'wire' section and send the notification
        # As this takes precedence over all other sections
        # (in case items appear in multiple sections)
        await _send_notification("wire", _get_users("wire"))

        # Next iterate over the registered sections (excluding wire and api)
        app = get_current_wsgi_app()
        for section_id in [
            section["_id"]
            for section in app.sections
            if section["_id"] != "wire" and section["group"] not in ["api", "monitoring"]
        ]:
            # Add the users for those sections and send the notification
            await _send_notification(section_id, _get_users(section_id))

    async def send_user_notification_emails(
        self, item: dict[str, Any], user_matches: list[ObjectId], users: dict[str, User], section: Any
    ):
        for user_id in user_matches:
            user = users.get(str(user_id))
            if is_canceled(item):
                await send_item_killed_notification_email(user, item=item)
            else:
                if user and user.get("receive_email"):
                    await send_history_match_notification_email(user, item=item, section=section)

    async def notify_agenda_topic_matches(
        self, item: dict[str, Any], users_dict: dict[str, User], companies_dict: dict[str, Company]
    ) -> Set[ObjectId]:
        topics = await get_topics_with_subscribers("agenda")
        topic_matches = get_resource_service("agenda").get_matching_topics(
            item["_id"], topics, users_dict, companies_dict
        )

        # Include topics where the ``query`` is ``item["_id"]``
        topic_matches.extend(
            [
                topic
                for topic in await get_agenda_notification_topics_for_query_by_id(item, users_dict)
                if topic.get("_id") not in topic_matches
            ]
        )

        if not topic_matches:
            return set()

        await push_agenda_item_notification("topic_matches", item=item, topics=topic_matches)
        return await self.send_topic_notification_emails(item, topics, topic_matches, users_dict, companies_dict)
