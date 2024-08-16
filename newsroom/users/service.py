from typing import Any, Dict

from superdesk.core import get_app_config
from superdesk.flask import request, abort
from superdesk.utils import is_hashed, get_hash
from superdesk.core.resources.service import ResourceModelType

from newsroom.signals import user_created
from newsroom.settings import get_setting
from newsroom.auth.utils import (
    get_company_auth_provider,
    is_current_user_admin,
    is_current_user_account_mgr,
    is_current_user_company_admin,
    send_token,
)
from newsroom.core.resources.service import NewshubAsyncResourceService

from .model import UserResourceModel
from .users import COMPANY_ADMIN_ALLOWED_PRODUCT_UPDATES, COMPANY_ADMIN_ALLOWED_UPDATES, USER_PROFILE_UPDATES


class UsersService(NewshubAsyncResourceService[UserResourceModel]):
    resource_name = "users"

    def get_model_instance_from_dict(self, data: Dict[str, Any]) -> ResourceModelType:
        """
        Override method to avoid validation issues with `signup_details` coming as string
        from already existing items in database. Also removing weird empty string "id" attribute
        """

        # remove legacy fields no longer user
        if "signup_details" in data:
            data.pop("signup_details")

        # removes attribute `id` that comes empty and breaks validation
        try:
            data.pop("id")
        except Exception:
            pass

        return super().get_model_instance_from_dict(data)

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

    async def check_permissions(self, user: UserResourceModel, updates=None):
        """Check if current user has permissions to edit user."""

        from .utils import get_user_async

        # TODO-ASYNC: figure out how to avoid accessing request here
        if not request or request.method == "GET":  # in behave there is test request context
            return

        # convert to dict first
        doc = user.model_dump(by_alias=True, exclude_unset=True)

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

    async def approve_user(self, user: UserResourceModel):
        """Approves & enables the supplied user, and sends an account validation email"""
        from .utils import get_company_from_user_or_session, get_token_data

        company = await get_company_from_user_or_session(user)
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
            send_token(updated_user, token_type="new_account", update_token=False)

    def _get_password_hash(self, password):
        return get_hash(password, get_app_config("BCRYPT_GENSALT_WORK_FACTOR", 12))
