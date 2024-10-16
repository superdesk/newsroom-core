from typing import Any
from datetime import timedelta, datetime, timezone
from logging import getLogger

from bson import ObjectId
from bson.errors import InvalidId
from quart_babel import gettext

from superdesk.core import get_current_app, get_app_config
from superdesk.core.types import Request
from superdesk.core.auth.user_auth import UserAuthProtocol
from superdesk.flask import url_for
from superdesk.utc import utcnow

from newsroom.types import CompanyResource, UserResourceModel, UserRole
from newsroom.flask import flash
from newsroom.companies import CompanyServiceAsync
from newsroom.users.service import UsersService


logger = getLogger(__name__)
SESSION_AUTH_TTL = timedelta(minutes=15)


class NewshubSessionAuth(UserAuthProtocol):
    async def authenticate(self, request: Request) -> Any | None:
        if not request.user:
            user_id = request.storage.session.get("user", "")
            if not user_id:
                await flash(gettext("Invalid username or password."), "danger")
                return await self.clear_session_and_redirect_to_login(request)

            try:
                user_id = ObjectId(user_id)
            except InvalidId:
                await flash(gettext("Invalid username or password."), "danger")
                return await self.clear_session_and_redirect_to_login(request)

            user: UserResourceModel = await UsersService().find_by_id(user_id)
            if not user:
                await flash(gettext("Invalid username or password."), "danger")
                return await self.clear_session_and_redirect_to_login(request)

            request.user = user
        company = await CompanyServiceAsync().find_by_id(request.user.company) if request.user.company else None

        if not await self.is_valid_session(request, request.user, company):
            return await self.clear_session_and_redirect_to_login(request)

        await self.continue_session(request, request.user, company=company)
        return None

    async def is_valid_session(
        self, request: Request, user: UserResourceModel, company: CompanyResource | None
    ) -> bool:
        # Get the current UTC time as a timezone-aware datetime
        now = datetime.now(timezone.utc)

        # Retrieve auth_ttl and ensure it is also timezone-aware
        auth_ttl = request.storage.session.get("auth_ttl")
        if not auth_ttl or not isinstance(auth_ttl, datetime):
            await flash(gettext("Invalid username or password."), "danger")
            return False

        if auth_ttl and auth_ttl.tzinfo is None:
            auth_ttl = auth_ttl.replace(tzinfo=timezone.utc)  # Make auth_ttl timezone-aware

        if not auth_ttl or auth_ttl < now:
            # Revalidate the user's session
            if company is None and user.user_type != UserRole.ADMINISTRATOR:
                await flash(gettext("Insufficient Permissions. Access denied."), "danger")
                return False
            elif not user.is_enabled:
                await flash(gettext("Account is disabled"), "danger")
                return False
            elif user.is_approved is False:
                approve_expiration = utcnow() - timedelta(days=get_app_config("NEW_ACCOUNT_ACTIVE_DAYS", 14))
                if user.created < approve_expiration:
                    # Account has not been approved
                    await flash(gettext("Account has not been approved"), "danger")
                    return False
            elif company is not None:
                if company.is_enabled is False:
                    await flash(gettext("Company account has been disabled."), "danger")
                    return False
                elif company.expiry_date and company.expiry_date.replace(tzinfo=None) <= datetime.utcnow().replace(
                    tzinfo=None
                ):
                    await flash(gettext("Company account has expired."), "danger")
                    return False
            request.storage.session.set("auth_ttl", utcnow().replace(tzinfo=None) + SESSION_AUTH_TTL)

        return True

    async def start_session(self, request: Request, user: UserResourceModel, **kwargs) -> None:
        request.storage.session.set("user", str(user.id))
        request.storage.session.set("name", f"{user.first_name} {user.last_name}")
        request.storage.session.set("user_type", user.user_type)
        request.storage.session.set("locale", user.locale)
        request.storage.session.set("auth_ttl", utcnow().replace(tzinfo=None) + SESSION_AUTH_TTL)

        if "permanent" in kwargs:
            request.storage.session.set_session_permanent(kwargs["permanent"])

        if not kwargs.get("company"):
            kwargs["company"] = await CompanyServiceAsync().find_by_id(user.company) if user.company else None

        await super().start_session(request, user, **kwargs)

    async def continue_session(self, request: Request, user: UserResourceModel, **kwargs) -> None:
        await super().continue_session(request, user, **kwargs)

        # Store user instance in the request storage,
        # to be used during the lifecycle of this request
        request.storage.request.set("user_instance", user)
        request.storage.request.set("company_instance", kwargs.get("company", None))

        if not user.last_active or user.last_active < utcnow() - timedelta(minutes=10):
            current_time = utcnow()
            updates = dict(
                last_active=current_time,
                is_validated=True,
            )
            await UsersService().system_update(user.id, updates)
            user.last_active = current_time
            user.is_validated = True
            get_current_app().as_any().cache.set(str(user.id), user.to_json())

    async def stop_session(self, request: "Request") -> None:
        await super().stop_session(request)
        request.storage.session.set("user", None)
        request.storage.session.set("name", None)
        request.storage.session.set("user_type", None)
        request.storage.session.set("locale", None)
        request.storage.session.set("auth_ttl", None)
        request.storage.request.pop("user_instance", None)
        request.storage.request.pop("company_instance", None)
        request.user = None

    def get_current_user(self, request: "Request") -> UserResourceModel | None:
        user_id = request.storage.session.get("user")
        if not user_id:
            # No user is currently logged in
            return None

        user = request.storage.request.get("user_instance")
        if not user:
            # UserResourceModel instance not currently cached in request storage
            # Get it from MongoDB directly and store it now
            user_dict = UsersService().mongo.find_one({"_id": ObjectId(user_id)})
            if not user_dict:
                # User not found, might be an invalid session
                return None

            user = UserResourceModel.from_dict(user_dict)
            request.storage.request.set("user_instance", user)

        if user and user.company and not request.storage.request.get("company_instance"):
            # CompanyResource instance not currently cached in request storage
            # Get it from MongoDB directly and store it now
            company_dict = CompanyServiceAsync().mongo.find_one({"_id": user.company})
            if company_dict:
                company = CompanyResource.from_dict(company_dict)
                request.storage.request.set("company_instance", company)

        return user

    async def clear_session_and_redirect_to_login(self, request: Request) -> Any:
        await self.stop_session(request)
        request.storage.session.set("next_url", request.url)
        return request.redirect(url_for("auth.login"))
