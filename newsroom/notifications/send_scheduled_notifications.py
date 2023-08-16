from typing import List, Dict, Any, Optional, TypedDict, Tuple
import logging
from datetime import datetime, timedelta
from copy import deepcopy

from bson import ObjectId
from flask import current_app as app

from superdesk import get_resource_service, Command
from superdesk.utc import utcnow, utc_to_local
from superdesk.celery_task_utils import get_lock_id
from superdesk.lock import lock, unlock, remove_locks

from newsroom.types import User, NotificationSchedule, Company, NotificationQueue, NotificationQueueTopic, Topic
from newsroom.utils import get_user_dict, get_company_dict
from newsroom.email import send_template_email
from newsroom.celery_app import celery
from newsroom.topics.topics import get_user_id_to_topic_for_subscribers
from newsroom.gettext import get_session_timezone, set_session_timezone

logger = logging.getLogger(__name__)


class NotificationEmailTopicEntry(TypedDict):
    topic: Topic
    item: Dict[str, Any]


class SendScheduledNotificationEmails(Command):
    def run(self, force: bool = False):
        self.log_msg = "Scheduled Notifications: {}".format(utcnow())

        logger.info(f"{self.log_msg} Starting to send scheduled notifications")

        lock_name = get_lock_id("newsroom", "send_scheduled_notifications")

        if not lock(lock_name, expire=610):
            logger.error(f"{self.log_msg} Job already running")
            return

        try:
            now_utc = utcnow().replace(second=0, microsecond=0)
            companies = get_company_dict(False)
            users = get_user_dict(False)
            user_topic_map = get_user_id_to_topic_for_subscribers()

            schedules: List[NotificationQueue] = get_resource_service("notification_queue").get(req=None, lookup={})
            for schedule in schedules:
                user = users.get(str(schedule["user"]))

                if not user:
                    # User not found, this account might be disabled
                    # Reset the queue for this user, so it does not get checked on future runs
                    get_resource_service("notification_queue").reset_queue(schedule["user"])
                    continue

                if not user.get("notification_schedule"):
                    user["notification_schedule"] = {}

                user["notification_schedule"].setdefault("timezone", get_session_timezone())
                user["notification_schedule"].setdefault("times", app.config["DEFAULT_SCHEDULED_NOTIFICATION_TIMES"])

                company = companies.get(str(user.get("company", "")))
                self.process_schedule(schedule, user, company, now_utc, user_topic_map.get(user["_id"]) or {}, force)
        except Exception as e:
            logger.exception(e)

        unlock(lock_name)
        remove_locks()

        logger.info(f"{self.log_msg} Completed sending scheduled notifications")

    def process_schedule(
        self,
        schedule: NotificationQueue,
        user: User,
        company: Optional[Company],
        now_utc: datetime,
        user_topics: Dict[ObjectId, Topic],
        force: bool,
    ):
        now_local = utc_to_local(user["notification_schedule"]["timezone"], now_utc)

        if not self._is_scheduled_to_run_for_user(user["notification_schedule"], now_local, force):
            return

        # Set the timezone on the session, so Babel is able to get the timezone for this user
        # when rendering the email, otherwise it uses the system default
        set_session_timezone(user["notification_schedule"]["timezone"])

        topic_entries: Dict[str, List[NotificationEmailTopicEntry]] = {
            "wire": [],
            "agenda": [],
        }

        topics_matched: List[ObjectId] = []
        topic_match_table: Dict[str, List[Tuple[str, int]]] = {
            "wire": [],
            "agenda": [],
        }

        if schedule.get("topics"):
            for section in ["wire", "agenda"]:
                for topic_queue in self._get_queue_entries_for_section(schedule, section):
                    if not len(topic_queue.get("items") or []):
                        # This Topic Queue didn't match any items during this period
                        continue

                    topic = user_topics.get(topic_queue["topic_id"])

                    if topic is None:
                        # Topic was not found for some reason
                        continue

                    latest_item = self._get_latest_item_from_topic_queue(topic_queue, topic, user, company)

                    if latest_item is None:
                        # Latest item was not found for some reason
                        continue

                    topics_matched.append(topic["_id"])
                    topic_match_table[section].append((topic["label"], len(topic_queue["items"])))
                    topic_entries[section].append(
                        NotificationEmailTopicEntry(
                            topic=topic,
                            item=latest_item,
                        )
                    )

        for topic_id, topic in user_topics.items():
            if topic["_id"] not in topics_matched:
                topic_match_table[topic["topic_type"]].append((topic["label"], 0))

        template_kwargs = dict(
            app_name=app.config["SITE_NAME"],
            entries=topic_entries,
            topic_match_table=topic_match_table,
            date=now_local,
        )

        if not len(topic_entries["wire"]) and not len(topic_entries["agenda"]):
            # No item's matched this topic queue, send an email indicating no matches
            send_template_email(
                to=[user["email"]],
                template="scheduled_notification_no_matches_email",
                template_kwargs=template_kwargs,
            )
        else:
            # Items matched this topic queue, send an email indicated matches
            send_template_email(
                to=[user["email"]],
                template="scheduled_notification_topic_matches_email",
                template_kwargs=template_kwargs,
            )

        # Now clear the topic match queue
        self._clear_user_notification_queue(user)

    def _is_scheduled_to_run_for_user(self, schedule: NotificationSchedule, now_local: datetime, force: bool):
        try:
            last_run_time_local = utc_to_local(schedule["timezone"], schedule["last_run_time"]).replace(
                second=0, microsecond=0
            )
        except KeyError:
            last_run_time_local = None

        if last_run_time_local is None and force:
            return True

        for schedule_datetime in self._convert_schedule_times(now_local, schedule["times"]):
            schedule_within_time = schedule_datetime - now_local < timedelta(minutes=5)

            if last_run_time_local is None and schedule_within_time:
                return True
            elif last_run_time_local is not None and last_run_time_local < schedule_datetime and schedule_within_time:
                return True

        return False

    def _clear_user_notification_queue(self, user: User):
        get_resource_service("notification_queue").reset_queue(user["_id"])
        get_resource_service("users").update_notification_schedule_run_time(user, utcnow())

    def _convert_schedule_times(self, now_local: datetime, times: List[str]) -> List[datetime]:
        schedule_datetimes: List[datetime] = []

        for time_str in times:
            time_parts = time_str.split(":")
            schedule_datetimes.append(now_local.replace(hour=int(time_parts[0]), minute=int(time_parts[1])))

        return schedule_datetimes

    def _get_queue_entries_for_section(self, queue: NotificationQueue, section: str) -> List[NotificationQueueTopic]:
        return sorted(
            [topic for topic in queue["topics"] if topic["section"] == section and topic.get("last_item_arrived")],
            key=lambda d: d["last_item_arrived"],
            reverse=True,
        )

    def _get_latest_item_from_topic_queue(
        self, topic_queue: NotificationQueueTopic, topic: Topic, user: User, company: Optional[Company]
    ) -> Optional[Dict[str, Any]]:
        for item_id in reversed(topic_queue["items"]):
            search_service = get_resource_service("wire_search" if topic["topic_type"] == "wire" else "agenda")

            section_filters = get_resource_service("section_filters").get_section_filters_dict()
            query = search_service.get_topic_query(
                topic, user, company, section_filters, args={"es_highlight": 1, "ids": [item_id]}
            )

            items = search_service.get_items_by_query(query, size=1)

            if items.count():
                return items[0]

        return None


@celery.task(soft_time_limit=600)
def send_scheduled_notifications():
    SendScheduledNotificationEmails().run()
