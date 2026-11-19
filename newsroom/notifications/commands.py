import logging
from collections import Counter
from bson import ObjectId
from datetime import datetime, timedelta
from time import monotonic
from typing import Any, TypedDict
from uuid import uuid4

from newsroom.users.service import UsersService
from superdesk.core import get_app_config
from superdesk.core.types import SearchRequest
from superdesk.utc import utcnow, utc_to_local
from superdesk.celery_task_utils import get_lock_id
from superdesk.lock import lock, unlock

from newsroom.types import (
    UserResourceModel,
    NotificationScheduleModel,
    CompanyResource,
    NotificationQueue,
    TopicResourceModel,
    Topic,
    NotificationType,
    NotificationTopic,
)
from newsroom.utils import get_user_dict_async, get_company_dict_async
from newsroom.email import send_user_email
from newsroom.celery_app import celery
from newsroom.topics.topics_async import get_user_id_to_topic_for_subscribers
from newsroom.gettext import get_session_timezone, set_session_timezone

from newsroom.wire import WireSearchServiceAsync, WireSearchRequestArgs
from newsroom.agenda import AgendaSearchServiceAsync, AgendaSearchRequestArgs

from .services import NotificationQueueService

logger = logging.getLogger(__name__)


class NotificationEmailTopicEntry(TypedDict):
    topic: Topic
    item: dict[str, Any]


TopicEntriesDict = dict[str, list[NotificationEmailTopicEntry]]

TopicMatchTable = dict[str, list[tuple[str, int]]]


class SendScheduledNotificationEmails:
    def __init__(self):
        self.log_msg = f"Scheduled Notifications: run_id={uuid4().hex}"
        self.stats: Counter[str] = Counter()

    async def run(self, force: bool = False):
        """
        Initiates the process to send scheduled notification emails. Acquires a lock
        to ensure no concurrent execution and invokes the schedule runner.
        """

        self.log_msg = f"Scheduled Notifications: run_id={uuid4().hex}"
        self.stats.clear()
        started = monotonic()
        logger.info(
            "%s Starting to send scheduled notifications now_utc=%s force=%s mail_suppress_send=%s testing=%s",
            self.log_msg,
            utcnow(),
            force,
            get_app_config("MAIL_SUPPRESS_SEND", None),
            get_app_config("TESTING", False),
        )

        lock_name = get_lock_id("newsroom", "send_scheduled_notifications")
        if not lock(lock_name, expire=610):
            logger.error("%s Skipping run reason=already_running", self.log_msg)
            return

        try:
            await self.run_schedules(force)
        except Exception:
            self.stats["failures"] += 1
            logger.exception("%s Error occurred while running scheduled notifications", self.log_msg)
        finally:
            unlock(lock_name)

        logger.info(
            "%s Completed scheduled notification run status=%s queues_examined=%s users_due=%s "
            "send_completed=%s skipped_not_due=%s skipped_inactive_or_missing=%s skipped_email=%s "
            "failures=%s duration_seconds=%.3f",
            self.log_msg,
            "completed_with_errors" if self.stats["failures"] else "completed",
            self.stats["queues_examined"],
            self.stats["users_due"],
            self.stats["send_completed"],
            self.stats["skipped_not_due"],
            self.stats["skipped_inactive_or_missing"],
            self.stats["skipped_email"],
            self.stats["failures"],
            monotonic() - started,
        )

    async def run_schedules(self, force: bool):
        """
        Retrieves and processes schedules for all users, running scheduled notifications.
        Handles missing user or company data and processes each schedule.
        """

        notification_queue_service = NotificationQueueService()

        try:
            now_utc = utcnow().replace(second=0, microsecond=0)
            companies = await get_company_dict_async(False)
            users = await get_user_dict_async(False)
            user_topic_map = await get_user_id_to_topic_for_subscribers(NotificationType.SCHEDULED)

            schedules_cursor = await notification_queue_service.search({})
            schedules = await schedules_cursor.to_list()
        except Exception:
            self.stats["failures"] += 1
            logger.exception("%s Failed to retrieve data to run schedules", self.log_msg)
            return

        for schedule in schedules:
            self.stats["queues_examined"] += 1
            try:
                user = users.get(schedule.user)

                if not user:
                    self.stats["skipped_inactive_or_missing"] += 1
                    logger.info(
                        "%s Skipping user=%s reason=user_missing_or_user_company_inactive_or_expired",
                        self.log_msg,
                        schedule.user,
                    )
                    # User not found, this account might be disabled
                    # Reset the queue for this user, so it does not get checked on future runs
                    await notification_queue_service.reset_queue(schedule.user)
                    logger.info(
                        "%s Queue cleared user=%s reason=user_missing_or_user_company_inactive_or_expired",
                        self.log_msg,
                        schedule.user,
                    )
                    continue

                if not user.notification_schedule:
                    # MyPy fails here with call-arg error, not sure why. Ignore it for now
                    user.notification_schedule = NotificationScheduleModel(  # type: ignore[call-arg]
                        timezone=get_session_timezone(),
                        times=[],
                    )

                if not user.notification_schedule.timezone:
                    user.notification_schedule.timezone = get_session_timezone()
                if not user.notification_schedule.times:
                    user.notification_schedule.times = get_app_config("DEFAULT_SCHEDULED_NOTIFICATION_TIMES")

                company = companies.get(user.company) if user.company else None
                await self.process_schedule(schedule, user, company, now_utc, user_topic_map.get(user.id) or {}, force)
            except Exception:
                self.stats["failures"] += 1
                logger.exception("%s Failed to run schedule for user=%s", self.log_msg, schedule.user)

    async def process_schedule(
        self,
        schedule: NotificationQueue,
        user: UserResourceModel,
        company: CompanyResource | None,
        now_utc: datetime,
        user_topics: dict[ObjectId, TopicResourceModel],
        force: bool,
    ):
        """
        Processes a user's notification schedule. Sends an email based on whether
        topics matched or not for the user's scheduled notification period.
        """
        timezone: str = (
            user.notification_schedule.timezone
            if user.notification_schedule and user.notification_schedule.timezone
            else get_session_timezone()
        )
        now_local = utc_to_local(timezone, now_utc)

        if not user.notification_schedule or not self.is_scheduled_to_run_for_user(
            user.notification_schedule, now_local, force
        ):
            self.stats["skipped_not_due"] += 1
            logger.debug(
                "%s Skipping user=%s reason=schedule_not_due timezone=%s now_local=%s times=%s last_run_time=%s",
                self.log_msg,
                user.id,
                timezone,
                now_local,
                user.notification_schedule.times if user.notification_schedule else [],
                user.notification_schedule.last_run_time if user.notification_schedule else None,
            )
            return

        self.stats["users_due"] += 1
        # Set the timezone on the session, so Babel is able to get the timezone for this user
        # when rendering the email, otherwise it uses the system default
        set_session_timezone(timezone)

        topic_entries, topic_match_table = await self.get_topic_entries_and_match_table(
            schedule, user, company, user_topics
        )

        template_kwargs = dict(
            app_name=get_app_config("SITE_NAME"),
            entries=topic_entries,
            topic_match_table=topic_match_table,
            date=now_utc,
        )

        if not len(topic_entries["wire"]) and not len(topic_entries["agenda"]):
            # No item's matched this topic queue, send an email indicating no matches
            template = "scheduled_notification_no_matches_email"
        else:
            # Items matched this topic queue, send an email indicated matches
            template = "scheduled_notification_topic_matches_email"

        logger.info(
            "%s Email send attempt user=%s template=%s queued_items=%s wire_entries=%s agenda_entries=%s timezone=%s",
            self.log_msg,
            user.id,
            template,
            sum(len(topic.items) for topic in schedule.topics),
            len(topic_entries["wire"]),
            len(topic_entries["agenda"]),
            timezone,
        )
        send_completed = await send_user_email(user, template=template, template_kwargs=template_kwargs)
        if send_completed:
            self.stats["send_completed"] += 1
            logger.info("%s Email send call completed user=%s template=%s", self.log_msg, user.id, template)
        else:
            self.stats["skipped_email"] += 1
            logger.info(
                "%s Email skipped user=%s template=%s reason=%s",
                self.log_msg,
                user.id,
                template,
                "user_disabled" if not user.is_enabled else "email_disabled",
            )

        # Now clear the topic match queue
        await self._clear_user_notification_queue(user)
        logger.info(
            "%s Queue cleared and last_run_time updated user=%s reason=%s",
            self.log_msg,
            user.id,
            "send_call_completed" if send_completed else "email_skipped",
        )

    def is_scheduled_to_run_for_user(
        self, schedule: NotificationScheduleModel, now_local: datetime, force: bool
    ) -> bool:
        """
        Determines if the notification schedule should run for the user based on their scheduled times
        and the current time.
        """

        last_run_time_local = (
            utc_to_local(schedule.timezone, schedule.last_run_time).replace(second=0, microsecond=0)
            if schedule.last_run_time is not None
            else None
        )

        if last_run_time_local is None and force:
            return True

        for schedule_datetime in self._convert_schedule_times(now_local, schedule.times):
            schedule_within_time = timedelta() <= now_local - schedule_datetime < timedelta(minutes=5)

            if last_run_time_local is None and schedule_within_time:
                return True
            elif last_run_time_local is not None and last_run_time_local < schedule_datetime and schedule_within_time:
                return True

        return False

    async def _clear_user_notification_queue(self, user: UserResourceModel):
        await NotificationQueueService().reset_queue(user.id)
        await UsersService().update_notification_schedule_run_time(user, utcnow())

    def _convert_schedule_times(self, now_local: datetime, times: list[str]) -> list[datetime]:
        schedule_datetimes: list[datetime] = []

        for time_str in times:
            time_parts = time_str.split(":")
            schedule_datetimes.append(now_local.replace(hour=int(time_parts[0]), minute=int(time_parts[1])))

        return schedule_datetimes

    def get_queue_entries_for_section(self, queue: NotificationQueue, section: str) -> list[NotificationTopic]:
        """
        Return the entries in the queue for a given section sorted by `last_item_arrived` attribute
        """

        return sorted(
            [topic for topic in queue.topics if topic.section == section and topic.last_item_arrived],
            key=lambda d: d.last_item_arrived,
            reverse=True,
        )

    async def get_latest_item_from_topic_queue(
        self,
        topic_queue: NotificationTopic,
        topic: TopicResourceModel,
        user: UserResourceModel,
        company: CompanyResource | None,
        exclude_items: set[str],
    ) -> dict[str, Any] | None:
        """
        Retrieves the latest item from a topic queue for the user and company, excluding specific items from the result.
        """

        for item_id in reversed(topic_queue.items):
            if item_id in exclude_items:
                continue

            search_service: AgendaSearchServiceAsync | WireSearchServiceAsync
            if topic.topic_type == "agenda":
                search_service = AgendaSearchServiceAsync()
                query = await search_service.get_topic_items_query(
                    topic, user, company, args=AgendaSearchRequestArgs(es_highlight=True, ids=[item_id], page_size=1)
                )
            else:
                search_service = WireSearchServiceAsync()
                query = await search_service.get_topic_items_query(
                    topic, user, company, args=WireSearchRequestArgs(es_highlight=True, ids=[item_id], page_size=1)
                )

            if not query:  # user might not have access to section anymore
                return None

            cursor = await search_service.service.find(SearchRequest(elastic=query))
            if await cursor.count():
                return await cursor.next_raw()

        return None

    async def get_topic_entries_and_match_table(
        self,
        schedule: NotificationQueue,
        user: UserResourceModel,
        company: CompanyResource | None,
        user_topics: dict[ObjectId, TopicResourceModel],
    ) -> tuple[TopicEntriesDict, TopicMatchTable]:
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

        topics_matched: list[ObjectId] = []
        topic_match_table: TopicMatchTable = {
            "wire": [],
            "agenda": [],
        }

        if not schedule.topics:
            return topic_entries, topic_match_table

        for section in ["wire", "agenda"]:
            items_in_entries: set[str] = set()

            for topic_queue in self.get_queue_entries_for_section(schedule, section):
                if not len(topic_queue.items):
                    # This Topic Queue didn't match any items during this period
                    continue

                topic = user_topics.get(topic_queue.topic_id)
                if topic is None:
                    # Topic was not found for some reason
                    continue

                topic_match_table[section].append((topic.label, len(topic_queue.items)))
                topics_matched.append(topic.id)

                latest_item = await self.get_latest_item_from_topic_queue(
                    topic_queue, topic, user, company, items_in_entries
                )

                if latest_item is None:
                    # Latest item was not found. It may have matched multiple topics
                    continue

                items_in_entries.add(latest_item["_id"])
                topic_entries[section].append(
                    NotificationEmailTopicEntry(
                        topic=topic.to_dict(),
                        item=latest_item,
                    )
                )

        for topic in user_topics.values():
            if topic.id not in topics_matched:
                topic_match_table[topic.topic_type].append((topic.label, 0))

        return topic_entries, topic_match_table


@celery.task(soft_time_limit=600)
async def send_scheduled_notifications():
    await SendScheduledNotificationEmails().run()
