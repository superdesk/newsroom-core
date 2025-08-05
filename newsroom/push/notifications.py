import logging

from typing import Any
from bson import ObjectId
import elasticapm

from superdesk.core.types import SearchRequest

from superdesk.core import get_app_config

from newsroom.core import get_current_wsgi_app
from newsroom.types import User, UserResourceModel, CompanyResource, TopicResourceModel, SectionEnum
from newsroom.history_async import get_history_users
from newsroom.utils import get_user_dict_async, get_company_dict_async
from newsroom.agenda.utils import push_agenda_item_notification
from newsroom.email import (
    send_new_item_notification_email,
    send_history_match_notification_email,
    send_item_killed_notification_email,
)
from newsroom.topics import (
    get_agenda_notification_topics_for_query_by_id,
    get_topics_with_subscribers_async,
)
from newsroom.notifications import push_notification, save_user_notifications, NotificationQueueService
from newsroom.wire import WireSearchServiceAsync
from newsroom.wire.filters import WireSearchRequestArgs
from newsroom.agenda import AgendaSearchServiceAsync
from newsroom.agenda.filters import AgendaSearchRequestArgs

logger = logging.getLogger(__name__)


def is_canceled(item: dict[str, Any]) -> bool:
    return item.get("pubstatus", item.get("state")) in ["canceled", "cancelled"]


class NotificationManager:
    async def notify_new_item(self, item: dict[str, Any], check_topics: bool = True):
        if not item or item.get("type") == "composite":
            return

        item_type = item.get("type")
        users_with_realtime_subscription: set[ObjectId] = set()
        try:
            users = await get_user_dict_async()
            user_ids = list(users.keys())

            companies = await get_company_dict_async()
            company_ids = list(companies.keys())

            if item_type == "agenda":
                await push_agenda_item_notification("new_item", item=item)
            else:
                push_notification("new_item", _items=[item])

            if check_topics:
                if item_type == "text":
                    users_with_realtime_subscription = await self.notify_wire_topic_matches(item, users, companies)
                else:
                    users_with_realtime_subscription = await self.notify_agenda_topic_matches(item, users, companies)

            if get_app_config("NOTIFY_MATCHING_USERS") == "never":
                return
            elif get_app_config("NOTIFY_MATCHING_USERS") == "cancel" and not is_canceled(item):
                return

            await self.notify_user_matches(
                item,
                users,
                companies,
                user_ids,
                company_ids,
                users_with_realtime_subscription if not is_canceled(item) else set(),
            )
        except Exception as e:
            logger.exception(e)
            logger.error(f"Failed to notify users for new {item_type} item", extra={"_id": item["_id"]})

    @elasticapm.capture_span()
    async def notify_wire_topic_matches(
        self, item: dict[str, Any], users: dict[ObjectId, UserResourceModel], companies: dict[ObjectId, CompanyResource]
    ) -> set[ObjectId]:
        logger.info("Finding matching topics for wire item %s", item["_id"])
        topics = await get_topics_with_subscribers_async("wire")
        topic_matches = await WireSearchServiceAsync().get_matching_topics_for_item(
            item["_id"], topics, list(users.values()), companies
        )

        if not topic_matches:
            return set()

        push_notification("topic_matches", item=item, topics=list(topic_matches))
        return await self.send_topic_notification_emails(item, topics, topic_matches, users, companies)

    async def send_topic_notification_emails(
        self,
        item: dict[str, Any],
        topics: list[TopicResourceModel],
        topic_matches: set[ObjectId],
        users: dict[ObjectId, UserResourceModel],
        companies: dict[ObjectId, CompanyResource],
    ) -> set[ObjectId]:
        users_processed: set[ObjectId] = set()
        users_with_realtime_subscription: set[ObjectId] = set()
        notification_queue_service = NotificationQueueService()

        for topic in topics:
            if topic.id not in topic_matches:
                continue

            for subscriber in topic.subscribers or []:
                try:
                    user = users.get(subscriber.user_id)

                    if not user:
                        continue

                    company = companies.get(user.company) if user.company else None

                    section: SectionEnum = topic.topic_type or SectionEnum.WIRE
                    if user.id not in users_processed:
                        # Only send websocket notification once for each item
                        await save_user_notifications(
                            [
                                dict(
                                    user=user.id,
                                    item=item["_id"],
                                    resource=section.value,
                                    action="topic_matches",
                                    data=None,
                                )
                            ]
                        )
                        users_processed.add(user.id)

                    if not user.receive_email:
                        continue
                    elif subscriber.notification_type == "scheduled":
                        await notification_queue_service.add_item_to_queue(user.id, section.value, topic.id, item)
                    elif user.id in users_with_realtime_subscription:
                        # This user has already received a realtime notification email about this item
                        # No need to send another
                        continue
                    else:
                        with elasticapm.capture_span("notify_user"):
                            users_with_realtime_subscription.add(user.id)
                            if topic.topic_type == SectionEnum.WIRE:
                                wire_service = WireSearchServiceAsync()
                                query = await wire_service.get_topic_items_query(
                                    topic,
                                    user,
                                    company,
                                    args=WireSearchRequestArgs(
                                        page_size=1,
                                        ids=[item["_id"]],
                                        es_highlight=True,
                                    ),
                                )
                                cursor = await wire_service.service.find(SearchRequest(elastic=query))
                                items = await cursor.to_list_raw()
                            else:
                                agenda_service = AgendaSearchServiceAsync()
                                query = await agenda_service.get_topic_items_query(
                                    topic,
                                    user,
                                    company,
                                    args=AgendaSearchRequestArgs(
                                        page_size=1,
                                        ids=[item["_id"]],
                                        es_highlight=True,
                                    ),
                                )
                                cursor = await agenda_service.service.find(SearchRequest(elastic=query))
                                items = await cursor.to_list_raw()
                            highlighted_item = item

                            if len(items) > 0:
                                highlighted_item = items[0]

                            await send_new_item_notification_email(
                                user,
                                topic.label,
                                item=highlighted_item,
                                section=section.value,
                            )
                except Exception as e:
                    logger.exception(e)
                    # when there is an error for specific topic/subscriber continue
                    continue

        return users_with_realtime_subscription

    async def notify_user_matches(
        self,
        item: dict[str, Any],
        users: dict[ObjectId, UserResourceModel],
        companies: dict[ObjectId, CompanyResource],
        user_ids: list[ObjectId],
        company_ids: list[ObjectId],
        users_with_realtime_subscription: set[ObjectId],
    ):
        """Send notification to users who have downloaded or bookmarked the provided item"""

        related_items: list[str] = item.get("ancestors", [])
        related_items.append(item["_id"])
        is_text = item.get("type") == "text"

        users_processed: set[ObjectId] = set()
        users_with_paused_notifications: set[ObjectId] = set(
            [user.id for user in users.values() if user.has_paused_notifications()]
        )

        async def _get_users(section: str) -> set[ObjectId]:
            """Get the list of users who have downloaded or bookmarked the items"""
            # Get users who have downloaded any of the items
            user_list = await get_history_users(related_items, user_ids, company_ids, section, "download")

            if is_text and section != "agenda":
                # Add users who have bookmarked any of the items
                bookmarked_users = await WireSearchServiceAsync().get_matching_item_bookmarks(
                    related_items,
                    users,
                    companies,
                )

                user_list.update(bookmarked_users)

            # Add users if this section is wire
            # Or if the user is not already in the list of users for wire
            # Removing duplicates, if any
            user_list = set(
                user_id
                for user_id in user_list
                if user_id not in users_processed
                and user_id not in users_with_realtime_subscription
                and user_id not in users_with_paused_notifications
            )

            users_processed.update(user_list)
            return user_list

        async def _send_notification(section: str, users_ids: set[ObjectId]):
            if not users_ids:
                return

            await save_user_notifications(
                [
                    dict(
                        user=user_id,
                        item=item["_id"],
                        resource=item.get("type") or item.get("_type"),
                        action="history_match",
                        data=None,
                    )
                    for user_id in users_ids
                ]
            )

            await self.send_user_notification_emails(item, users_ids, users, section)

        # First add users for the 'wire' section and send the notification
        # As this takes precedence over all other sections
        # (in case items appear in multiple sections)
        await _send_notification("wire", await _get_users("wire"))

        # Next iterate over the registered sections (excluding wire and api)
        app = get_current_wsgi_app()
        for section_id in [
            section["_id"]
            for section in app.sections
            if section["_id"] != "wire" and section["group"] not in ["api", "monitoring"]
        ]:
            # Add the users for those sections and send the notification
            await _send_notification(section_id, await _get_users(section_id))

    @elasticapm.capture_span()
    async def send_user_notification_emails(
        self, item: dict[str, Any], user_matches: set[ObjectId], users: dict[ObjectId, UserResourceModel], section: str
    ):
        logger.info("Sending topic notifications for item %s", item["_id"])
        for user_id in user_matches:
            user = users.get(user_id)
            if not user:
                continue
            elif is_canceled(item):
                await send_item_killed_notification_email(user, item=item)
            else:
                if user.receive_email:
                    await send_history_match_notification_email(user, item=item, section=section)

    @elasticapm.capture_span()
    async def notify_agenda_topic_matches(
        self, item: dict[str, Any], users: dict[ObjectId, UserResourceModel], companies: dict[ObjectId, CompanyResource]
    ) -> set[ObjectId]:
        logger.info("Finding matching topics for agenda item %s", item["_id"])
        topics = await get_topics_with_subscribers_async("agenda")

        topic_matches = await AgendaSearchServiceAsync().get_matching_topics_for_item(
            item["_id"], topics, list(users.values()), companies
        )

        # Include topics where the ``query`` is ``item["_id"]``
        users_dict: dict[str, User] = {str(user.id): user.to_dict() for user in users.values()}
        topic_matches |= set(
            [
                topic["_id"]
                for topic in await get_agenda_notification_topics_for_query_by_id(item, users_dict)
                if topic.get("_id") not in topic_matches
            ]
        )

        if not topic_matches:
            return set()

        await push_agenda_item_notification("topic_matches", item=item, topics=list(topic_matches))
        return await self.send_topic_notification_emails(item, topics, topic_matches, users, companies)
