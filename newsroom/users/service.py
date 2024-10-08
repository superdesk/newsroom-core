import pytz
from copy import deepcopy
from datetime import datetime, date
from typing import Any, Dict

from quart_babel import gettext
from werkzeug.exceptions import BadRequest

from newsroom.types import User
from superdesk.core import get_app_config
from superdesk.flask import request, abort, session
from superdesk.utils import is_hashed, get_hash

from newsroom.settings import get_setting
from newsroom.auth.utils import (
    get_company_auth_provider,
    is_current_user_admin,
    is_current_user_account_mgr,
    is_current_user_company_admin,
    send_token,
)
from newsroom.core import get_current_wsgi_app
from newsroom.signals import user_created, user_updated, user_deleted
from newsroom.core.resources.service import NewshubAsyncResourceService
from newsroom.companies.utils import get_updated_products, get_updated_sections

from .model import UserResourceModel
from .users import COMPANY_ADMIN_ALLOWED_PRODUCT_UPDATES, COMPANY_ADMIN_ALLOWED_UPDATES, USER_PROFILE_UPDATES


class UsersService(NewshubAsyncResourceService[UserResourceModel]):
    resource_name = "users"

    async def on_create(self, docs):
        await super().on_create(docs)

        for doc in docs:
            await self.check_permissions(doc)

            if doc.password and not is_hashed(doc.password):
                doc.password = self._get_password_hash(doc.password)

    async def on_created(self, docs):
        await super().on_created(docs)
        for doc in docs:
            user_created.send(self, user=doc)

    async def on_update(self, updates, original):
        from .utils import get_company_from_user

        await self.check_permissions(original, updates)
        if "password" in updates:
            updates["password"] = self._get_password_hash(updates["password"])

        company_id = updates.get("company", original.company)
        company = await get_company_from_user({"company": company_id})
        company_changed = updates.get("company") and updates["company"] != original.company

        if company_changed or "sections" in updates or "products" in updates:
            # Company, Sections or Products have changed, recalculate the list of sections & products
            updates["sections"] = get_updated_sections(updates, original, company)
            updates["products"] = get_updated_products(updates, original, company)

        app = get_current_wsgi_app()
        app.cache.delete(str(original.id))
        app.cache.delete(original.email)

    async def on_updated(self, updates, original):
        from .utils import get_user_id

        # set session locale if updating locale for current user
        if updates.get("locale") and original.id == get_user_id() and updates["locale"] != original.locale:
            session["locale"] = updates["locale"]

        updated = original.model_copy(update=updates)
        user_updated.send(self, user=updated, updates=updates)

    async def on_deleted(self, doc):
        get_current_wsgi_app().cache.delete(str(doc.id))
        user_deleted.send(self, user=doc.to_dict())

    async def on_delete(self, doc):
        from .utils import get_user_id

        if doc.id == get_user_id():
            raise BadRequest(gettext("Can not delete current user"))

        user = await self.find_by_id(doc.id)
        await self.check_permissions(user)
        super().on_delete(doc)

    async def check_permissions(self, user: UserResourceModel, updates=None):
        """Check if current user has permissions to edit user."""

        from .utils import get_user_async

        # TODO-ASYNC: figure out how to avoid accessing request here
        if not request or request.method == "GET":  # in behave there is test request context
            return

        # convert to dict first
        doc = user.to_dict()

        if is_current_user_admin() or is_current_user_account_mgr():
            return

        if request.url_rule and request.url_rule.rule:
            if request.url_rule.rule in ["/reset_password/<token>", "/token/<token_type>"]:
                return

        # Only check against metadata that has changed from the original
        updated_fields = (
            []
            if updates is None
            else [field for field in updates.keys() if updates[field] != doc.get(field) and field != "id"]
        )

        if is_current_user_company_admin():
            manager = await get_user_async()
            if manager and manager.company == user.company:
                allowed_updates = (
                    COMPANY_ADMIN_ALLOWED_UPDATES
                    if not get_setting("allow_companies_to_manage_products")
                    else COMPANY_ADMIN_ALLOWED_UPDATES.union(COMPANY_ADMIN_ALLOWED_PRODUCT_UPDATES)
                )

                if not updated_fields:
                    return
                elif all([key in allowed_updates for key in updated_fields]):
                    return
                elif request and request.method == "DELETE" and doc.get("_id") != manager.get("_id"):
                    return

        if request.method != "DELETE" and (
            not updated_fields or all([key in USER_PROFILE_UPDATES for key in updated_fields])
        ):
            return

        abort(403)

    async def update_notification_schedule_run_time(self, user: dict[str, Any], run_time: datetime):
        """
        Updates the user's notification schedule with the provided run time and clears related cache.

        Args:
            user: The user object containing the current notification schedule.
            run_time: The new run time to be updated in the notification schedule.
        """
        notification_schedule = deepcopy(user["notification_schedule"])
        notification_schedule["last_run_time"] = run_time
        await self.update(user["_id"], {"notification_schedule": notification_schedule})

        app = self.app.wsgi
        app.cache.delete(str(user["_id"]))
        app.cache.delete(user["email"])

    async def approve_user(self, user: UserResourceModel):
        """Approves & enables the supplied user, and sends an account validation email"""
        from .utils import get_company_from_user_or_session, get_token_data

        company_as_dict = None
        company = await get_company_from_user_or_session(user)
        if company:
            company_as_dict = company.to_dict()

        auth_provider = get_company_auth_provider(company_as_dict)

        user_updates: Dict[str, Any] = {
            "is_enabled": True,
            "is_approved": True,
        }

        if auth_provider.features["verify_email"]:
            token_data = get_token_data()
            user_updates["token"] = token_data.get("token") or ""
            user_updates["token_expiry_date"] = token_data.get("token_expiry_date")

        await self.update(user.id, user_updates)

        # Send new account / password reset email
        if auth_provider.features["verify_email"]:
            updated_user = user.model_copy(update=user_updates).to_dict()
            await send_token(updated_user, token_type="new_account", update_token=False)

    def _get_password_hash(self, password):
        return get_hash(password, get_app_config("BCRYPT_GENSALT_WORK_FACTOR", 12))

    async def system_update(self, item_id, updates):
        await self.mongo.update_one({"_id": item_id}, {"$set": updates})
        try:
            await self.elastic.update(item_id, updates)
        except KeyError:
            pass

    @classmethod
    def user_has_paused_notifications(cls, user: User) -> bool:
        schedule = user.get("notification_schedule") or {}
        timezone = pytz.timezone(schedule.get("timezone") or get_app_config("DEFAULT_TIMEZONE") or "UTC")
        pause_from = schedule.get("pause_from")
        pause_to = schedule.get("pause_to")

        if pause_from and pause_to:
            now = datetime.now(timezone).date()
            pause_from_date = date.fromisoformat(pause_from)
            pause_to_date = date.fromisoformat(pause_to)

            if pause_from_date <= now <= pause_to_date:
                return True

        return False
