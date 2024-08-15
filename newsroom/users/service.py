from typing import Any, Dict
from superdesk.flask import request, abort
from superdesk.core.resources.service import ResourceModelType

from newsroom.auth import get_user
from newsroom.settings import get_setting
from newsroom.auth.utils import is_current_user_admin, is_current_user_account_mgr, is_current_user_company_admin
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
        if data.get("signup_details") == "":
            data["signup_details"] = {}

        # removes emptry string attribute `id` that breaks validation
        try:
            data.pop("id")
        except:
            pass

        return super().get_model_instance_from_dict(data)

    def check_permissions(self, doc, updates=None):
        """Check if current user has permissions to edit user."""
        if not request or request.method == "GET":  # in behave there is test request context
            return

        if is_current_user_admin() or is_current_user_account_mgr():
            return

        # Only check against metadata that has changed from the original
        updated_fields = (
            []
            if updates is None
            else [field for field in updates.keys() if updates[field] != doc.get(field) and field != "id"]
        )

        if request.url_rule and request.url_rule.rule:
            if request.url_rule.rule in ["/reset_password/<token>", "/token/<token_type>"]:
                return

        if is_current_user_company_admin():
            manager = get_user()
            if doc.get("company") and doc["company"] == manager.get("company"):
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
