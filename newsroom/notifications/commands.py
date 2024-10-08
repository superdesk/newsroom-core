import logging
from bson import ObjectId
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, TypedDict, Tuple, Set, cast

from newsroom.users.service import UsersService
from superdesk.core import get_app_config
from superdesk import get_resource_service
from superdesk.utc import utcnow, utc_to_local
from superdesk.celery_task_utils import get_lock_id
from superdesk.lock import lock, unlock

from newsroom.types import User, NotificationSchedule, Company, Topic
from newsroom.utils import get_user_dict, get_company_dict
from newsroom.email import send_user_email
from newsroom.celery_app import celery
from newsroom.topics.topics_async import get_user_id_to_topic_for_subscribers, NotificationType
from newsroom.gettext import get_session_timezone, set_session_timezone

from .services import NotificationQueueService
from .models import NotificationQueue, NotificationTopic

logger = logging.getLogger(__name__)


class NotificationEmailTopicEntry(TypedDict):
    topic: Topic
    item: Dict[str, Any]


TopicEntriesDict = Dict[str, List[NotificationEmailTopicEntry]]

TopicMatchTable = Dict[str, List[Tuple[str, int]]]


class SendScheduledNotificationEmails:
    async def run(self, force: bool = False):
        """
        Initiates the process to send scheduled notification emails. Acquires a lock
        to ensure no concurrent execution and invokes the schedule runner.
        """

        self.log_msg = "Scheduled Notifications: {}".format(utcnow())
        logger.info(f"{self.log_msg} Starting to send scheduled notifications")

        lock_name = get_lock_id("newsroom", "send_scheduled_notifications")
        if not lock(lock_name, expire=610):
            logger.error("Send scheduled notifications task already running")
            return

        try:
            await self.run_schedules(force)
        except Exception as e:
            logger.exception("Error occurred while running scheduled notifications: %s", e)
        finally:
            unlock(lock_name)

        logger.info(f"{self.log_msg} Completed sending scheduled notifications")

    async def run_schedules(self, force: bool):
        """
        Retrieves and processes schedules for all users, running scheduled notifications.
        Handles missing user or company data and processes each schedule.
        """

        notification_queue_service = NotificationQueueService()

        try:
            now_utc = utcnow().replace(second=0, microsecond=0)
            companies = await get_company_dict(False)
            users = await get_user_dict(False)
            user_topic_map = await get_user_id_to_topic_for_subscribers(NotificationType.SCHEDULED)

            schedules_cursor = await notification_queue_service.search({})
            schedules = await schedules_cursor.to_list()
        except Exception as e:
            logger.exception(e)
            logger.error("Failed to retrieve data to run schedules")
            return

        for schedule in schedules:
            user_id = schedule.user
            try:
                user = users.get(str(user_id))

                if not user:
                    # User not found, this account might be disabled
                    # Reset the queue for this user, so it does not get checked on future runs
                    await notification_queue_service.reset_queue(schedule.user)
                    continue

                if not user.get("notification_schedule"):
                    user["notification_schedule"] = {}

                user["notification_schedule"].setdefault("timezone", await get_session_timezone())
                user["notification_schedule"].setdefault(
                    "times", get_app_config("DEFAULT_SCHEDULED_NOTIFICATION_TIMES")
                )

                company = companies.get(str(user.get("company", "")))
                await self.process_schedule(
                    schedule, user, company, now_utc, user_topic_map.get(user["_id"]) or {}, force
                )
            except Exception as e:
                logger.exception(e)
                logger.error("Failed to run schedule for user %s", user_id)

    async def process_schedule(
        self,
        schedule: NotificationQueue,
        user: User,
        company: Optional[Company],
        now_utc: datetime,
        user_topics: Dict[ObjectId, Topic],
        force: bool,
    ):
        """
        Processes a user's notification schedule. Sends an email based on whether
        topics matched or not for the user's scheduled notification period.
        """

        now_local = utc_to_local(user["notification_schedule"]["timezone"], now_utc)

        if not self.is_scheduled_to_run_for_user(user["notification_schedule"], now_local, force):
            return

        # Set the timezone on the session, so Babel is able to get the timezone for this user
        # when rendering the email, otherwise it uses the system default
        set_session_timezone(user["notification_schedule"]["timezone"])

        topic_entries, topic_match_table = self.get_topic_entries_and_match_table(schedule, user, company, user_topics)

        template_kwargs = dict(
            app_name=get_app_config("SITE_NAME"),
            entries=topic_entries,
            topic_match_table=topic_match_table,
            date=now_utc,
        )

        if not len(topic_entries["wire"]) and not len(topic_entries["agenda"]):
            # No item's matched this topic queue, send an email indicating no matches
            await send_user_email(
                user,
                template="scheduled_notification_no_matches_email",
                template_kwargs=template_kwargs,
            )
        else:
            # Items matched this topic queue, send an email indicated matches
            await send_user_email(
                user,
                template="scheduled_notification_topic_matches_email",
                template_kwargs=template_kwargs,
            )

        # Now clear the topic match queue
        await self._clear_user_notification_queue(user)

    def is_scheduled_to_run_for_user(self, schedule: NotificationSchedule, now_local: datetime, force: bool):
        """
        Determines if the notification schedule should run for the user based on their scheduled times
        and the current time.
        """

        try:
            last_run_time_local = utc_to_local(schedule["timezone"], schedule["last_run_time"]).replace(
                second=0, microsecond=0
            )
        except KeyError:
            last_run_time_local = None

        if last_run_time_local is None and force:
            return True

        for schedule_datetime in self._convert_schedule_times(now_local, schedule["times"]):
            schedule_within_time = timedelta() <= now_local - schedule_datetime < timedelta(minutes=5)

            if last_run_time_local is None and schedule_within_time:
                return True
            elif last_run_time_local is not None and last_run_time_local < schedule_datetime and schedule_within_time:
                return True

        return False

    async def _clear_user_notification_queue(self, user: User):
        await NotificationQueueService().reset_queue(user["_id"])
        await UsersService().update_notification_schedule_run_time(cast(dict, user), utcnow())

    def _convert_schedule_times(self, now_local: datetime, times: List[str]) -> List[datetime]:
        schedule_datetimes: List[datetime] = []

        for time_str in times:
            time_parts = time_str.split(":")
            schedule_datetimes.append(now_local.replace(hour=int(time_parts[0]), minute=int(time_parts[1])))

        return schedule_datetimes

    def get_queue_entries_for_section(self, queue: NotificationQueue, section: str) -> List[NotificationTopic]:
        """
        Return the entries in the queue for a given section sorted by `last_item_arrived` attribute
        """

        return sorted(
            [topic for topic in queue.topics if topic.section == section and topic.last_item_arrived],
            key=lambda d: d.last_item_arrived,
            reverse=True,
        )

    def get_latest_item_from_topic_queue(
        self,
        topic_queue: NotificationTopic,
        topic: Topic,
        user: User,
        company: Optional[Company],
        exclude_items: Set[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves the latest item from a topic queue for the user and company, excluding specific items from the result.
        """

        for item_id in reversed(topic_queue.items):
            if item_id in exclude_items:
                continue

            # TODO-ASYNC: update when `wire_search` is migrated to async
            search_service = get_resource_service("wire_search" if topic["topic_type"] == "wire" else "agenda")

            query = search_service.get_topic_query(topic, user, company, args={"es_highlight": 1, "ids": [item_id]})

            if not query:  # user might not have access to section anymore
                return None

            items = search_service.get_items_by_query(query, size=1)

            if items.count():
                return items[0]

        return None

    def get_topic_entries_and_match_table(
        self,
        schedule: NotificationQueue,
        user: User,
        company: Optional[Company],
        user_topics: Dict[ObjectId, Topic],
    ) -> Tuple[TopicEntriesDict, TopicMatchTable]:
        """
        Generates the topic entries and a match table for a user's scheduled notifications.

        This method processes the notification queue and matches topics based on user preferences and available topics.

        It returns two key outputs:
        - `topic_entries`: A dictionary containing lists of matched topics from the 'wire' and 'agenda' sections that
        will be included in the notification email.
        - `topic_match_table`: A table indicating the topics that matched items and the number of items found per topic.
        """

        topic_entries: TopicEntriesDict = {
            "wire": [],
            "agenda": [],
        }

        topics_matched: List[ObjectId] = []
        topic_match_table: TopicMatchTable = {
            "wire": [],
            "agenda": [],
        }

        if not schedule.topics:
            return topic_entries, topic_match_table

        for section in ["wire", "agenda"]:
            items_in_entries: Set[str] = set()

            for topic_queue in self.get_queue_entries_for_section(schedule, section):
                if not len(topic_queue.items):
                    # This Topic Queue didn't match any items during this period
                    continue

                topic = user_topics.get(topic_queue.topic_id)
                if topic is None:
                    # Topic was not found for some reason
                    continue

                topic_match_table[section].append((topic["label"], len(topic_queue.items)))
                topics_matched.append(topic["_id"])

                latest_item = self.get_latest_item_from_topic_queue(topic_queue, topic, user, company, items_in_entries)

                if latest_item is None:
                    # Latest item was not found. It may have matched multiple topics
                    continue

                items_in_entries.add(latest_item["_id"])
                topic_entries[section].append(
                    NotificationEmailTopicEntry(
                        topic=topic,
                        item=latest_item,
                    )
                )

        for _, topic in user_topics.items():
            if topic["_id"] not in topics_matched:
                topic_match_table[topic["topic_type"]].append((topic["label"], 0))

        return topic_entries, topic_match_table


@celery.task(soft_time_limit=600)
async def send_scheduled_notifications():
    await SendScheduledNotificationEmails().run()
