# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015, 2016, 2017, 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import datetime
import logging

from superdesk.utc import utcnow
from superdesk.celery_task_utils import get_lock_id
from superdesk.lock import lock, unlock

from newsroom.celery_app import celery
from newsroom.email import send_user_email
from newsroom.settings import get_settings_collection, GENERAL_SETTINGS_LOOKUP


logger = logging.getLogger(__name__)


class CompanyExpiryAlerts:
    async def send_alerts(self):
        self.log_msg = "Company Expiry Alerts: {}".format(utcnow())
        logger.info("{} Starting to send alerts.".format(self.log_msg))

        lock_name = get_lock_id("newsroom", "company_expiry")
        if not lock(lock_name, expire=610):
            logger.error("Company expiry alert task already running")
            return

        try:
            await self.worker()
        except Exception as e:
            logger.exception(e)
        finally:
            unlock(lock_name)

        logger.info(f"{self.log_msg} Completed sending alerts.")

    async def worker(self):
        from newsroom.email import send_template_email
        from newsroom.companies import CompanyServiceAsync
        from newsroom.users import UsersService

        # Check if there are any recipients
        general_settings = get_settings_collection().find_one(GENERAL_SETTINGS_LOOKUP)
        try:
            recipients = general_settings["values"]["company_expiry_alert_recipients"].split(",")
        except (KeyError, TypeError):
            logger.warning("there are no alert expiry recipients")
            return

        expiry_time = (utcnow() + datetime.timedelta(days=7)).replace(hour=0, minute=0, second=0)
        companies_service = CompanyServiceAsync()

        companies_cursor = await companies_service.search({"expiry_date": {"$lte": expiry_time}, "is_enabled": True})
        companies = await companies_cursor.to_list_raw()

        if (await companies_cursor.count()) > 0:
            users_service = UsersService()

            # Send notifications to users who are nominated to receive expiry alerts
            for company in companies:
                users_cursor = await users_service.search({"company": company.id, "expiry_alert": True})

                if (await users_cursor.count()) > 0:
                    template_kwargs = {
                        "expiry_date": company.expiry_date,
                        "expires_on": company.expiry_date.strftime("%d-%m-%Y"),
                    }
                    logger.info(f"{self.log_msg} Sending to following users of company {company.name}: {recipients}")

                    async for user in users_cursor.to_list():
                        await send_user_email(
                            user,
                            template="company_expiry_alert_user",
                            template_kwargs=template_kwargs,
                        )

            if not (general_settings.get("values") or {}).get("company_expiry_alert_recipients"):
                return  # No one else to send

            template_kwargs = {
                "companies": sorted(companies, key=lambda k: k["expiry_date"]),
                "expiry_date": expiry_time,
                "expires_on": expiry_time.strftime("%d-%m-%Y"),
            }
            logger.info("{} Sending to following expiry administrators: {}".format(self.log_msg, recipients))
            await send_template_email(
                to=recipients,
                template="company_expiry_email",
                template_kwargs=template_kwargs,
            )


@celery.task(soft_time_limit=600)
def company_expiry():
    CompanyExpiryAlerts().send_alerts()
