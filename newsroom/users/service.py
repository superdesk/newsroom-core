import pytz
from copy import deepcopy
from datetime import datetime, date
from typing import Any, Dict

import re
from quart_babel import gettext
from werkzeug.exceptions import BadRequest

from newsroom.types import User
from superdesk.core import get_app_config
from superdesk.core.types import HTTP_METHOD, Request
from superdesk.flask import abort
from superdesk.utils import is_hashed, get_hash

from newsroom.types import UserResourceModel, UserAuthResourceModel
from newsroom.exceptions import AuthorizationError
from newsroom.settings import get_setting
from newsroom.auth.utils import (
    is_from_request,
    get_current_request,
    get_user_from_request,
    get_user_or_none_from_request,
    get_user_id_from_request,
    get_company_auth_provider,
    get_token_data,
    send_token,
)
from newsroom.core import get_current_wsgi_app
from newsroom.signals import user_created, user_updated, user_deleted
from newsroom.core.resources.service import NewshubAsyncResourceService
from newsroom.companies import CompanyServiceAsync
from newsroom.companies.utils import get_updated_products, get_updated_sections

from .users import COMPANY_ADMIN_ALLOWED_PRODUCT_UPDATES, COMPANY_ADMIN_ALLOWED_UPDATES, USER_PROFILE_UPDATES


class UsersService(NewshubAsyncResourceService[UserResourceModel]):
    resource_name = "users"

    async def authorize(self, request: Request):
        current_user = get_user_or_none_from_request(request)
        requested_user_id = request.get_view_args("item_id")

        if current_user and requested_user_id:
            if current_user == requested_user_id:
                # Request is for editing the currently logged-in user
                return
            elif current_user.is_company_admin():
                # Request is for editing a different user, and current user is CompanyAdmin
                requested_user = await self.find_by_id(requested_user_id)
                if requested_user and requested_user.company == current_user.company:
                    return

        raise AuthorizationError(403, gettext("Unauthorized to edit another user"), title=gettext("403. Forbidden"))

    async def on_create(self, docs):
        await super().on_create(docs)

        for doc in docs:
            await self.check_permissions(doc, None, "POST")

    async def on_created(self, docs):
        await super().on_created(docs)
        for doc in docs:
            user_created.send(self, user=doc)

    async def on_update(self, updates, original):
        await super().on_update(updates, original)
        await self.check_permissions(original, updates, "PATCH")

        company_id = updates.get("company", original.company)
        company_changed = updates.get("company") and updates["company"] != original.company

        if company_changed or "sections" in updates or "products" in updates:
            # Company, Sections or Products have changed, recalculate the list of sections & products
            company = await CompanyServiceAsync().find_by_id(company_id)
            updates["sections"] = get_updated_sections(updates, original, company)
            updates["products"] = get_updated_products(updates, original, company)

        app = get_current_wsgi_app()
        app.cache.delete(str(original.id))
        app.cache.delete(original.email)

    async def on_updated(self, updates: dict[str, Any], original: UserResourceModel):
        if is_from_request():
            # If this is from a request, test to see if we need to update the
            # current user cached in request storage
            current_request = get_current_request()
            current_user = get_user_from_request(current_request)
            if current_user and original.id == current_user.id:
                updated = original.to_dict()
                updated.update(updates)
                updated_user = UserResourceModel.from_dict(updated)
                current_request.storage.request.set("user_instance", updated_user)

                if updated_user.locale != original.locale:
                    current_request.storage.session.set("locale", updated_user.locale)

        updated = original.model_copy(update=updates)
        user_updated.send(self, user=updated, updates=updates)

    async def on_deleted(self, doc):
        get_current_wsgi_app().cache.delete(str(doc.id))
        user_deleted.send(self, user=doc.to_dict())

    async def on_delete(self, doc):
        if doc.id == get_user_id_from_request(None):
            raise BadRequest(gettext("Can not delete current user"))

        user = await self.find_by_id(doc.id)
        await self.check_permissions(user, None, "DELETE")
        await super().on_delete(doc)

    async def check_permissions(self, user: UserResourceModel, updates: dict | None, method: HTTP_METHOD):
        """Check if current user has permissions to edit user."""

        if not is_from_request():
            # This is not coming from a request through the API but internally
            # Unable to determine the current user
            return

        current_user = get_user_or_none_from_request(None)
        if not current_user or current_user.is_admin() or current_user.is_account_manager():
            return

        user_dict = user.to_dict()

        # Only check against metadata that has changed from the original
        updated_fields = (
            []
            if updates is None
            else [field for field in updates.keys() if updates[field] != user_dict.get(field) and field != "id"]
        )

        if current_user.is_company_admin() and current_user.company == user.company:
            allowed_updates = (
                COMPANY_ADMIN_ALLOWED_UPDATES
                if not get_setting("allow_companies_to_manage_products")
                else COMPANY_ADMIN_ALLOWED_UPDATES.union(COMPANY_ADMIN_ALLOWED_PRODUCT_UPDATES)
            )

            if not updated_fields:
                return
            elif all([key in allowed_updates for key in updated_fields]):
                return
            elif method == "DELETE" and user.id != current_user.id:
                return

        if method != "DELETE" and (not updated_fields or all([key in USER_PROFILE_UPDATES for key in updated_fields])):
            return

        abort(403)

    async def get_by_email(self, email: str) -> UserResourceModel | None:
        lookup = {"$regex": re.compile("^{}$".format(re.escape(email)), re.IGNORECASE)}
        return await self.find_one(email=lookup)

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

    @staticmethod
    def user_has_paused_notifications(user: User) -> bool:
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


class UsersAuthService(NewshubAsyncResourceService[UserAuthResourceModel]):
    async def on_create(self, docs: list[UserAuthResourceModel]) -> None:
        await super().on_create(docs)
        for doc in docs:
            if doc.password and not is_hashed(doc.password):
                doc.password = self._get_password_hash(doc.password)

    async def on_created(self, docs):
        await super().on_created(docs)
        for doc in docs:
            user_created.send(self, user=doc)

    async def on_update(self, updates: dict[str, Any], original: UserAuthResourceModel) -> None:
        await super().on_update(updates, original)
        if "password" in updates:
            updates["password"] = self._get_password_hash(updates["password"])

        app = get_current_wsgi_app()
        app.cache.delete(str(original.id))
        app.cache.delete(original.email)

    async def on_updated(self, updates: dict[str, Any], original: UserAuthResourceModel):
        updated = original.model_copy(update=updates)
        user_updated.send(self, user=updated, updates=updates)

    async def on_deleted(self, doc):
        get_current_wsgi_app().cache.delete(str(doc.id))
        user_deleted.send(self, user=doc.to_dict())

    def _get_password_hash(self, password):
        return get_hash(password, get_app_config("BCRYPT_GENSALT_WORK_FACTOR", 12))

    async def get_by_email(self, email: str) -> UserAuthResourceModel | None:
        lookup = {"$regex": re.compile("^{}$".format(re.escape(email)), re.IGNORECASE)}
        return await self.find_one(email=lookup)

    async def approve_user(self, user: UserAuthResourceModel):
        """Approves & enables the supplied user, and sends an account validation email"""

        company = await user.get_company()
        auth_provider = get_company_auth_provider(company)

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
            updated_user = user.model_copy(update=user_updates)
            await send_token(updated_user, token_type="new_account", update_token=False)
