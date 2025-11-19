# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015, 2016, 2017, 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import base64
import os
from datetime import datetime, timedelta
import logging
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import Dict, Any, List

from superdesk.core import get_app_config, get_current_app, get_current_async_app
from superdesk.core.resources.cursor import ResourceCursorAsync
from superdesk.utc import utcnow, utc_to_local, local_to_utc
from superdesk.celery_task_utils import get_lock_id
from superdesk.lock import lock, unlock

from newsroom.types import MonitoringProfileResourceModel, UserResourceModel
from newsroom.formatters import get_formatter
from newsroom.celery_app import celery
from newsroom.email import send_user_email, send_template_email, EmailAttachment, EmailKwargs
from newsroom.settings import get_settings_collection, GENERAL_SETTINGS_LOOKUP
from newsroom.utils import parse_date_str
from newsroom.search.types import NewshubSearchRequest
from newsroom.history_async import HistoryService

from .service import MonitoringProfileService
from .search import MonitoringSearchService, MonitoringSearchRequestArgs
from .utils import get_monitoring_file, truncate_article_body, get_date_items_dict
from ..wire.embeds import remove_all_embeds

logger = logging.getLogger(__name__)


@dataclass
class AlertMonitoringDataEntry:
    w_lists: list[MonitoringProfileResourceModel]
    created_from: str
    created_from_time: str


async def send_email_alert(
    items: list[Dict[str, Any]],
    monitoring_profile: MonitoringProfileResourceModel,
    users: List[UserResourceModel],
    general_settings: Dict[str, Any],
) -> None:
    """
    Send an email immediate alert with the details in the body of the email. If a logo image is set in the
    monitoring_report_logo_path settings it will be attached to the email and can be referenced in the
    monitoring_export.html template as <img src="CID:logo" />
    :param items:
    :param monitoring_profile:
    :param users: List of users to receive the email alert
    :param general_settings: Dictionary of setting passed to avoid having to read them again
    :return:
    """

    # If there is only one story to send and the headline is to be used as the subject
    if monitoring_profile.headline_subject and len(items) == 1:
        monitoring_profile.subject = items[0].get("headline", monitoring_profile.subject or monitoring_profile.name)

    data = {
        "date_items_dict": get_date_items_dict(items),
        "monitoring_profile": monitoring_profile,
        "current_date": utc_to_local(get_app_config("DEFAULT_TIMEZONE"), utcnow()).strftime("%d/%m/%Y"),
        "monitoring_report_name": get_app_config("MONITORING_REPORT_NAME", "Newsroom"),
    }

    # Attach logo to email if defined
    kwargs: EmailKwargs = {}
    if general_settings and general_settings["values"].get("monitoring_report_logo_path"):
        image_filename = general_settings["values"].get("monitoring_report_logo_path")
        if os.path.exists(image_filename):
            with open(image_filename, "rb") as img:
                bts = base64.b64encode(img.read())
                logo: EmailAttachment = {
                    "file": bts,
                    "file_name": "logo{}".format(os.path.splitext(image_filename)[1]),
                    "file_desc": "Logo",
                    "content_type": "image/{}".format(os.path.splitext(image_filename)[1].replace(".", "")),
                    "headers": {"Content-ID": "logo"},
                }
                kwargs["attachments_info"] = [logo]
    if monitoring_profile.email:
        to_list = [t.strip() for t in monitoring_profile.email.split(",")]
        await send_template_email(to=to_list, template="monitoring_export", template_kwargs=data, cc=None, **kwargs)
    for user in users:
        await send_user_email(user, template="monitoring_export", template_kwargs=data, **kwargs)


class MonitoringEmailAlerts:
    def __init__(self):
        self.log_msg = f"Monitoring Scheduled Alerts: {utcnow()}"

    async def run(self, immediate: bool = False) -> None:
        try:
            get_current_async_app().resources.get_resource_service("monitoring")
        except KeyError:
            logger.info(f"{self.log_msg} Monitoring app is not enabled! Not sending email alerts")
            return

        logger.info(f"{self.log_msg} Starting to send alerts.")

        lock_name = get_lock_id(
            "newsroom",
            "monitoring_{0}".format("scheduled" if not immediate else "immediate"),
        )
        if not lock(lock_name, expire=610):
            logger.error("Monitoring email alerts task already running")
            return

        try:
            now_local = utc_to_local(get_app_config("DEFAULT_TIMEZONE"), utcnow())
            get_current_app().config["SERVER_NAME"] = celery.conf["SERVER_NAME"] = (
                urlparse(get_app_config("CLIENT_URL")).netloc or None
            )

            now_to_minute = now_local.replace(second=0, microsecond=0)

            if immediate:
                await self.immediate_worker(now_to_minute)
            else:
                await self.scheduled_worker(now_to_minute)
        except Exception as e:
            logger.exception(e)
        finally:
            unlock(lock_name)

        logger.info("{} Completed sending Monitoring Scheduled Alerts.".format(self.log_msg))

    async def immediate_worker(self, now: datetime) -> None:
        last_minute = now - timedelta(minutes=1)
        default_timezone = get_app_config("DEFAULT_TIMEZONE")
        await self.send_alerts(
            await self.get_immediate_monitoring_list(),
            local_to_utc(default_timezone, last_minute).strftime("%Y-%m-%d"),
            local_to_utc(default_timezone, last_minute).strftime("%H:%M:%S"),
            now,
        )

    async def get_scheduled_monitoring_list(self) -> ResourceCursorAsync[MonitoringProfileResourceModel]:
        return await MonitoringProfileService().search(
            {
                "schedule.interval": {"$in": ["one_hour", "two_hour", "four_hour", "weekly", "daily"]},
                "is_enabled": True,
            }
        )

    async def get_immediate_monitoring_list(self) -> list[MonitoringProfileResourceModel]:
        cursor = await MonitoringProfileService().search(
            {
                "schedule.interval": "immediate",
                "is_enabled": True,
            }
        )
        return await cursor.to_list()

    async def scheduled_worker(self, now: datetime) -> None:
        monitoring_list = await self.get_scheduled_monitoring_list()

        one_hour_ago = now - timedelta(hours=1)
        two_hours_ago = now - timedelta(hours=2)
        four_hours_ago = now - timedelta(hours=4)
        yesterday = now - timedelta(days=1)
        last_week = now - timedelta(days=7)

        default_timezone = get_app_config("DEFAULT_TIMEZONE")
        one_hours_ago_utc = local_to_utc(default_timezone, one_hour_ago)
        two_hours_ago_utc = local_to_utc(default_timezone, two_hours_ago)
        four_hours_ago_utc = local_to_utc(default_timezone, four_hours_ago)
        yesterday_utc = local_to_utc(default_timezone, yesterday)
        last_week_utc = local_to_utc(default_timezone, last_week)

        alert_monitoring: dict[str, AlertMonitoringDataEntry] = dict(
            one=AlertMonitoringDataEntry(
                w_lists=[],
                created_from=one_hours_ago_utc.strftime("%Y-%m-%d"),
                created_from_time=one_hours_ago_utc.strftime("%H:%M:%S"),
            ),
            two=AlertMonitoringDataEntry(
                w_lists=[],
                created_from=two_hours_ago_utc.strftime("%Y-%m-%d"),
                created_from_time=two_hours_ago_utc.strftime("%H:%M:%S"),
            ),
            four=AlertMonitoringDataEntry(
                w_lists=[],
                created_from=four_hours_ago_utc.strftime("%Y-%m-%d"),
                created_from_time=four_hours_ago_utc.strftime("%H:%M:%S"),
            ),
            daily=AlertMonitoringDataEntry(
                w_lists=[],
                created_from=yesterday_utc.strftime("%Y-%m-%d"),
                created_from_time=yesterday_utc.strftime("%H:%M:%S"),
            ),
            weekly=AlertMonitoringDataEntry(
                w_lists=[],
                created_from=last_week_utc.strftime("%Y-%m-%d"),
                created_from_time=last_week_utc.strftime("%H:%M:%S"),
            ),
        )

        async for monitoring_profile in monitoring_list:
            self.add_to_send_list(
                alert_monitoring,
                monitoring_profile,
                now,
                one_hour_ago,
                two_hours_ago,
                four_hours_ago,
                yesterday,
                last_week,
            )

        for key, value in alert_monitoring.items():
            await self.send_alerts(value.w_lists, value.created_from, value.created_from_time, now)

    def is_within_five_minutes(self, new_scheduled_time: datetime, now: datetime) -> bool:
        return (new_scheduled_time - now).total_seconds() < 300

    def is_past_range(self, last_run_time: datetime | None, upper_range: datetime) -> bool:
        return not last_run_time or last_run_time < upper_range

    def add_to_send_list(
        self,
        alert_monitoring: dict[str, AlertMonitoringDataEntry],
        profile: MonitoringProfileResourceModel,
        now: datetime,
        one_hour_ago: datetime,
        two_hours_ago: datetime,
        four_hours_ago: datetime,
        yesterday: datetime,
        last_week: datetime,
    ):
        if profile.schedule is None:
            # This should not happen, as we're filtering specifically for monitoring profiles with a schedule
            # but the schedule is optional, and the type dictates it could be `None`, so trap that scenario here
            return

        last_run_time = parse_date_str(profile.last_run_time) if profile.last_run_time else None
        default_timezone = get_app_config("DEFAULT_TIMEZONE")
        if last_run_time:
            last_run_time = utc_to_local(default_timezone, last_run_time)

        # Convert time to current date for range comparison
        if profile.schedule.time:
            hour_min = profile.schedule.time.split(":")
            schedule_today_plus_five_mins = utc_to_local(default_timezone, utcnow())
            schedule_today_plus_five_mins = schedule_today_plus_five_mins.replace(
                hour=int(hour_min[0]), minute=int(hour_min[1])
            )
            schedule_today_plus_five_mins = schedule_today_plus_five_mins + timedelta(minutes=5)

            # Check if the time window is according to schedule
            if (
                profile.schedule.interval == "daily"
                and self.is_within_five_minutes(schedule_today_plus_five_mins, now)
                and self.is_past_range(last_run_time, yesterday)
            ):
                alert_monitoring["daily"].w_lists.append(profile)
                return

            # Check if the time window is according to schedule
            # Check if 'day' is according to schedule
            if (
                profile.schedule.interval == "weekly"
                and self.is_within_five_minutes(schedule_today_plus_five_mins, now)
                and schedule_today_plus_five_mins.strftime("%a").lower() == profile.schedule.day
                and self.is_past_range(last_run_time, last_week)
            ):
                alert_monitoring["weekly"].w_lists.append(profile)
                return
        else:
            # Check if current time is within 'hourly' window
            if now.minute > 4:
                return

            if profile.schedule.interval == "one_hour" and self.is_past_range(last_run_time, one_hour_ago):
                alert_monitoring["one"].w_lists.append(profile)
                return

            if (
                profile.schedule.interval == "two_hour"
                and now.hour % 2 == 0
                and self.is_past_range(last_run_time, two_hours_ago)
            ):
                alert_monitoring["two"].w_lists.append(profile)
                return

            if (
                profile.schedule.interval == "four_hour"
                and now.hour % 4 == 0
                and self.is_past_range(last_run_time, four_hours_ago)
            ):
                alert_monitoring["four"].w_lists.append(profile)
                return

    async def already_sent(self, item: Dict[str, Any], profile: MonitoringProfileResourceModel) -> bool:
        #     """
        #     Checks the history for this item/version being sent by the profile already
        #     :param item:
        #     :param profile:
        #     :return: True if any matching found
        #     """
        version_to_query = item.get("version") or item.get("_current_version", "")
        lookup = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"action": "email"}},
                        {"term": {"item": item.get("_id")}},
                        {"term": {"version": version_to_query}},
                        {"term": {"monitoring": profile.id}},
                        {"term": {"company": profile.company}},
                    ]
                }
            }
        }
        return (await HistoryService().count(lookup=lookup)) > 0

    async def send_alerts(
        self,
        monitoring_list: list[MonitoringProfileResourceModel],
        created_from: str,
        created_from_time: str,
        now: datetime,
    ):
        general_settings = get_settings_collection().find_one(GENERAL_SETTINGS_LOOKUP)
        error_recipients = []
        if general_settings and general_settings["values"].get("system_alerts_recipients"):
            error_recipients = general_settings["values"]["system_alerts_recipients"].split(",")

        from newsroom.email import send_template_email
        from newsroom.users import UsersService
        from newsroom.companies import CompanyServiceAsync

        users_service = UsersService()
        companies_service = CompanyServiceAsync()

        for monitoring_data in monitoring_list:
            last_run_time = local_to_utc(get_app_config("DEFAULT_TIMEZONE"), now)
            if monitoring_data.schedule is None:
                # This should not happen, as we're filtering specifically for monitoring profiles with a schedule
                # but the schedule is optional, and the type dictates it could be `None`, so trap that scenario here
                continue

            if monitoring_data.format_type is None:
                # If for some reason this Monitoring Profile does not have a ``format_type`` set
                # then we default it to ``monitoring_pdf``
                monitoring_data.format_type = "monitoring_pdf"

            if (monitoring_data.users and len(monitoring_data.users)) or monitoring_data.email:
                users: List[UserResourceModel] = []
                if monitoring_data.users and len(monitoring_data.users):
                    users = await users_service.find_items_by_ids(monitoring_data.users)
                company = (
                    await companies_service.find_by_id(monitoring_data.company) if monitoring_data.company else None
                )
                if company is None:
                    logger.exception(f"Company {monitoring_data.company} not found!")
                    continue

                if not company.is_enabled:
                    logger.warning(
                        f'Company "{monitoring_data.company}" for profile "{monitoring_data.name}" is disabled!'
                    )
                    continue

                # if immediate set the created from to the time of the last item set in the profile, if available
                if monitoring_data.schedule.interval == "immediate" and monitoring_data.last_run_time:
                    start_date = monitoring_data.last_run_time.strftime("%Y-%m-%d")
                    start_time = monitoring_data.last_run_time.strftime("%H:%M:%S")
                else:
                    start_date = created_from
                    start_time = created_from_time

                search_request = NewshubSearchRequest(
                    args=MonitoringSearchRequestArgs(
                        navigation_ids=[monitoring_data.id],
                        skip_user_validation=True,
                        start_date=start_date,
                        start_time=start_time,
                    ),
                    company=company,
                )
                cursor = await MonitoringSearchService().search(search_request)
                items = await cursor.to_list_raw()
                # remove any items that have already been sent
                items[:] = [item for item in items if not await self.already_sent(item, monitoring_data)]
                template_kwargs = {"profile": monitoring_data.to_dict()}
                for item in items:
                    remove_all_embeds(item)
                if items:
                    try:
                        template_kwargs.update(
                            {
                                "items": items,
                                "section": "wire",
                            }
                        )
                        truncate_article_body(items, monitoring_data)
                        if monitoring_data.format_type == "monitoring_email":
                            await send_email_alert(items, monitoring_data, users, general_settings)
                        else:
                            kwargs: EmailKwargs = {}
                            monitoring_file = await get_monitoring_file(monitoring_data, items)
                            attachment = base64.b64encode(monitoring_file.read())
                            formatter = get_formatter(monitoring_data.format_type)
                            attachments_info: EmailAttachment = {
                                "file": attachment,
                                "file_name": formatter.format_filename(None),
                                "content_type": "application/{}".format(formatter.FILE_EXTENSION),
                                "file_desc": "Monitoring Report for Celery monitoring alerts for profile: {}".format(
                                    monitoring_data.name
                                ),
                                "headers": {},
                            }
                            kwargs["attachments_info"] = [attachments_info]
                            if monitoring_data.email:
                                to_list = [t.strip() for t in monitoring_data.email.split(",")]
                                await send_template_email(
                                    to=to_list,
                                    template="monitoring_email",
                                    template_kwargs=template_kwargs,
                                    cc=None,
                                    **kwargs,
                                )
                            for user in users:
                                await send_user_email(
                                    user,
                                    template="monitoring_email",
                                    template_kwargs=template_kwargs,
                                    **kwargs,
                                )
                        await HistoryService().create_history_record(
                            items,
                            action="email",
                            user_id=None,
                            company_id=monitoring_data.company,
                            section="monitoring",
                            monitoring_id=monitoring_data.id,
                        )
                    except Exception:
                        logger.exception(
                            f"{self.log_msg} Error processing monitoring profile {monitoring_data.name} for company {company.name}."
                        )
                        if error_recipients:
                            # Send an email to admin
                            template_kwargs = {
                                "profile": monitoring_data.to_dict(),
                                "name": monitoring_data.name,
                                "company": company.name,
                                "run_time": now,
                            }
                            await send_template_email(
                                to=error_recipients,
                                template="monitoring_error",
                                template_kwargs=template_kwargs,
                            )
                elif monitoring_data.schedule.interval != "immediate" and monitoring_data.always_send:
                    for user in users:
                        await send_user_email(
                            user,
                            template="monitoring_email_no_updates",
                            template_kwargs=template_kwargs,
                        )

                # for immediate schedules we set the last_run_time to the versioncreated of the last item.
                # with an additional grace period in case an item is late getting to Newshub or previouse run
                # exceeds the soft time out or dies with the lock!
                if monitoring_data.schedule.interval == "immediate":
                    if len(items):
                        last_article_created = max(parse_date_str(item.get("versioncreated")) for item in items)
                        if last_article_created:
                            last_run_time = last_article_created - timedelta(minutes=11)
                    elif monitoring_data.last_run_time is None:
                        last_run_time = last_run_time - timedelta(minutes=11)
                    else:  # don't override the last_run_time if no items were found
                        last_run_time = None
            if last_run_time:
                await MonitoringProfileService().update(monitoring_data.id, {"last_run_time": last_run_time})


@celery.task(soft_time_limit=600)
async def monitoring_schedule_alerts():
    await MonitoringEmailAlerts().run()


@celery.task(soft_time_limit=600)
async def monitoring_immediate_alerts():
    await MonitoringEmailAlerts().run(True)
