import re
import json
import pymongo
from copy import deepcopy
from typing import Any, Dict, Optional
from pydantic import BaseModel, field_validator

from bson import ObjectId
from flask_babel import gettext
from werkzeug.exceptions import BadRequest, NotFound

from newsroom.users.service import UsersService
from superdesk import get_resource_service
from superdesk.core.web import Request, Response
from superdesk.core import get_current_app, get_app_config
from superdesk.flask import jsonify, abort, session

from newsroom.user_roles import UserRole
from newsroom.auth import get_user_by_email, get_company
from newsroom.auth.utils import (
    get_auth_providers,
    send_token,
    add_token_data,
    is_current_user_admin,
    is_current_user,
    is_current_user_account_mgr,
    is_current_user_company_admin,
    get_company_auth_provider,
)
from newsroom.settings import get_setting
from newsroom.decorator import admin_only, login_required, account_manager_or_company_admin_only
from newsroom.companies import (
    get_company_sections_monitoring_data,
)
from newsroom.notifications.notifications import get_notifications_with_items
from newsroom.topics import get_user_topics
from newsroom.users import blueprint
from newsroom.users.forms import UserForm
from newsroom.users.users import (
    COMPANY_ADMIN_ALLOWED_UPDATES,
    COMPANY_ADMIN_ALLOWED_PRODUCT_UPDATES,
    USER_PROFILE_UPDATES,
)
from newsroom.utils import query_resource, find_one, get_json_or_400, get_vocabulary, success_response
from newsroom.monitoring.views import get_monitoring_for_company
from newsroom.ui_config_async import UiConfigResourceService

from .module import users_endpoints
from .utils import get_company_from_user_or_session, get_user_or_abort, get_company_from_user


def get_settings_data():
    app = get_current_app().as_any()

    return {
        "users": list(query_resource("users")),
        "companies": list(query_resource("companies")),
        "sections": app.sections,
        "products": list(query_resource("products")),
        "countries": app.countries,
        "auth_provider_features": {key: provider.features for key, provider in get_auth_providers().items()},
    }


async def get_view_data():
    user = await get_user_or_abort()
    user_as_dict = user.model_dump(by_alias=True, exclude_unset=True)

    company = await get_company_from_user_or_session(user)
    company_as_dict = company.model_dump(by_alias=True, exclude_unset=True)

    auth_provider = get_company_auth_provider(company_as_dict)
    ui_config_service = UiConfigResourceService()

    user_company = await get_company_from_user(user)

    view_data = {
        "user": user_as_dict,
        "company": company.id or "",
        "topics": get_user_topics(user.id) if user else [],
        "companyName": user_company.name or "",
        "locators": get_vocabulary("locators"),
        "ui_configs": await ui_config_service.get_all_config(),
        "groups": get_app_config("WIRE_GROUPS", []),
        "authProviderFeatures": dict(auth_provider.features),
    }

    if get_app_config("ENABLE_MONITORING"):
        # TODO-ASYNC: update when monitoring app is moved to async
        view_data["monitoring_list"] = get_monitoring_for_company(user_as_dict)

    view_data.update(await get_company_sections_monitoring_data(company, user))

    return view_data


class WhereParam(BaseModel):
    company: Optional[str] = None
    products_id: Optional[str] = None

    @field_validator("company", "products_id", mode="after")
    def convert_to_objectid(cls, value):
        if value is not None:
            return ObjectId(value)
        return value


class ObjectIdListModel(BaseModel):
    ids: Optional[str] = None

    @field_validator("ids", mode="after")
    def split_and_convert_ids(cls, value):
        if isinstance(value, str):
            return [ObjectId(id_str) for id_str in value.split(",")]
        return value


class SearchArgs(ObjectIdListModel):
    q: Optional[str] = None
    sort: Optional[str] = None
    where: Optional[WhereParam] = None

    @field_validator("where", mode="before")
    def parse_where(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        return value


@users_endpoints.endpoint("/users/search", methods=["GET"])
@account_manager_or_company_admin_only
async def search(args: None, params: SearchArgs, request: Request) -> Response:
    lookup: Dict[str, Any] = {}
    sort = None

    if params.q:
        regex = re.compile(re.escape(params.q), re.IGNORECASE)
        lookup = {"$or": [{"first_name": regex}, {"last_name": regex}, {"email": regex}]}

    if params.ids:
        lookup = {"_id": {"$in": params.ids}}

    if params.sort:
        sort = params.sort

    where_param = params.where

    if where_param:
        if where_param.company:
            lookup["company"] = where_param.company
        if where_param.products_id:
            lookup["products._id"] = where_param.products_id

    # Make sure this request only searches for the current users company
    if is_current_user_company_admin():
        company = await get_company_from_user_or_session()
        if company:
            lookup["company"] = company.id
        else:
            request.abort(401)

    mongo_cursor = await UsersService().search(lookup, use_mongo=True)

    # TODO-ASYNC: we need to implement the sorting somehow within the base service
    # When using mongo, the `AsyncIOMotorCollection.find` supports an additional
    # parameter `sort` for sorting.
    if sort:
        mongo_cursor.cursor.sort(sort, pymongo.ASCENDING)

    users = await mongo_cursor.to_list_raw()

    return Response(users, 200, ())


@users_endpoints.endpoint("/users/new", methods=["POST"])
@account_manager_or_company_admin_only
def create():
    form = UserForm()
    if form.validate():
        if not _is_email_address_valid(form.email.data):
            return jsonify({"email": [gettext("Email address is already in use")]}), 400

        new_user = get_updates_from_form(form, on_create=True)
        user_is_company_admin = is_current_user_company_admin()
        if user_is_company_admin:
            company = get_company()
            if company is None:
                abort(401)

            # Make sure this new user is associated with ``company`` and as a ``PUBLIC`` user
            new_user["company"] = company["_id"]
            new_user["user_type"] = UserRole.PUBLIC.value
        elif form.company.data:
            new_user["company"] = ObjectId(form.company.data)
        elif new_user["user_type"] != "administrator":
            return (
                jsonify({"company": [gettext("Company is required for non administrators")]}),
                400,
            )

        # Flask form won't accept default value if any form data was passed in the request.
        # So, we need to set this explicitly here.
        new_user["receive_email"] = True
        new_user["receive_app_notifications"] = True

        company = get_company(new_user)
        auth_provider = get_company_auth_provider(company)

        if auth_provider.features["verify_email"]:
            add_token_data(new_user)

        ids = get_resource_service("users").post([new_user])

        if auth_provider.features["verify_email"]:
            send_token(new_user, token_type="new_account", update_token=False)

        return jsonify({"success": True, "_id": ids[0]}), 201
    return jsonify(form.errors), 400


@blueprint.route("/users/<_id>/resend_invite", methods=["POST"])
@account_manager_or_company_admin_only
def resent_invite(_id):
    user = find_one("users", _id=ObjectId(_id))
    company = get_company()
    user_is_company_admin = is_current_user_company_admin()
    auth_provider = get_company_auth_provider(get_company(user))

    if not user:
        return NotFound(gettext("User not found"))
    elif user.get("is_validated"):
        return jsonify({"is_validated": gettext("User is already validated")}), 400
    elif user_is_company_admin and (company is None or user["company"] != ObjectId(company["_id"])):
        # Company admins can only resent invites for members of their company only
        abort(403)
    elif not auth_provider.features["verify_email"]:
        # Can only regenerate new token if ``verify_email`` is enabled in ``AuthProvider``
        abort(403)

    send_token(user, token_type="new_account")
    return jsonify({"success": True}), 200


def _is_email_address_valid(email):
    # TODO-ASYNC: update once `auth` is migrated to async
    existing_user = get_user_by_email(email)
    return not existing_user


class RouteArguments(BaseModel):
    user_id: str


@users_endpoints.endpoint("/users/<string:user_id>", methods=["GET", "POST"])
@login_required
async def edit(args: RouteArguments, params: None, request: Request):
    user_is_company_admin = is_current_user_company_admin()
    user_is_admin = is_current_user_admin()
    user_is_account_mgr = is_current_user_account_mgr()
    user_is_non_admin = not (user_is_company_admin or user_is_admin or user_is_account_mgr)

    if not (user_is_admin or user_is_account_mgr or user_is_company_admin) and not is_current_user(args.user_id):
        request.abort(401)

    user = await UsersService().find_by_id(args.user_id)
    company = await get_company_from_user_or_session()

    if user_is_company_admin and (company is None or user.company != company._id):
        request.abort(403)

    if not user:
        return NotFound(gettext("User not found"))

    etag = request.get_header("If-Match")
    if etag and user.etag != etag:
        request.abort(412)

    if request.method == "POST":
        form = UserForm(user=user)

        if form.validate_on_submit():
            if form.email.data != user.email and not _is_email_address_valid(form.email.data):
                return Response({"email": [gettext("Email address is already in use")]}, 400, ())

            elif not user_is_company_admin and not form.company.data and form.user_type.data != "administrator":
                return Response({"company": [gettext("Company is required for non administrators")]}, 400, ())

            updates = get_updates_from_form(form)

            if not user_is_admin and updates.get("user_type", "") != (user.user_type or ""):
                request.abort(401)

            allowed_fields = None
            if user_is_non_admin:
                allowed_fields = USER_PROFILE_UPDATES
            elif user_is_company_admin:
                # TODO-ASYNC: adjust when `get_setting` is migrated to async
                allowed_fields = (
                    COMPANY_ADMIN_ALLOWED_UPDATES
                    if not get_setting("allow_companies_to_manage_products")
                    else COMPANY_ADMIN_ALLOWED_UPDATES.union(COMPANY_ADMIN_ALLOWED_PRODUCT_UPDATES)
                )

            if allowed_fields is not None:
                for field in list(updates.keys()):
                    if field not in allowed_fields:
                        updates.pop(field, None)

            await UsersService().update(args.user_id, updates=updates)

            return success_response({"success": True})

        return Response(form.errors, 400, ())

    return success_response(user)


def get_updates_from_form(form: UserForm, on_create=False):
    updates = form.data
    if form.company.data:
        updates["company"] = ObjectId(form.company.data)
    if "sections" in updates:
        if on_create and not updates.get("sections"):
            updates.pop("sections")  # will be populated later based on company
        elif updates.get("sections") is not None:
            updates["sections"] = {
                section["_id"]: section["_id"] in (form.sections.data or [])
                for section in get_current_app().as_any().sections
            }

    if updates.get("products") is not None:
        product_ids = [ObjectId(productId) for productId in updates["products"]]
        products = {
            product["_id"]: product for product in query_resource("products", lookup={"_id": {"$in": product_ids}})
        }
        updates["products"] = [
            {"_id": product["_id"], "section": product["product_type"]} for product in products.values()
        ]
    return updates


@blueprint.route("/users/<_id>/profile", methods=["POST"])
@login_required
def edit_user_profile(_id):
    if not is_current_user(_id):
        abort(403)

    user_id = ObjectId(_id)
    user = find_one("users", _id=user_id)

    if not user:
        return NotFound(gettext("User not found"))

    form = UserForm(user=user)
    if form.validate_on_submit():
        updates = {key: val for key, val in form.data.items() if key in USER_PROFILE_UPDATES}
        get_resource_service("users").patch(user_id, updates=updates)
        return jsonify({"success": True}), 200
    return jsonify(form.errors), 400


@blueprint.route("/users/<_id>/notification_schedules", methods=["POST"])
@login_required
def edit_user_notification_schedules(_id):
    if not is_current_user(_id):
        abort(403)

    user_id = ObjectId(_id)
    user = find_one("users", _id=user_id)

    if not user:
        return NotFound(gettext("User not found"))

    data = get_json_or_400()

    updates = {"notification_schedule": deepcopy(user.get("notification_schedule") or {})}
    updates["notification_schedule"].update(data)
    get_resource_service("users").patch(user_id, updates=updates)
    return jsonify({"success": True}), 200


@blueprint.route("/users/<_id>/validate", methods=["POST"])
@admin_only
def validate(_id):
    return _resend_token(_id, token_type="validate")


@blueprint.route("/users/<_id>/reset_password", methods=["POST"])
@account_manager_or_company_admin_only
def resend_token(_id):
    return _resend_token(_id, token_type="reset_password")


def _resend_token(user_id, token_type):
    """
    Sends a new token for a given user_id
    :param user_id: Id of the user to send the token
    :param token_type: validate or reset_password
    :return:
    """
    if not user_id:
        return BadRequest(gettext("User id not provided"))

    user = find_one("users", _id=ObjectId(user_id))

    if not user:
        return NotFound(gettext("User not found"))

    if send_token(user, token_type):
        return jsonify({"success": True}), 200

    return jsonify({"message": "Token could not be sent"}), 400


@blueprint.route("/users/<_id>", methods=["DELETE"])
@account_manager_or_company_admin_only
def delete(_id):
    """Deletes the user by given id"""
    get_resource_service("users").delete_action({"_id": ObjectId(_id)})
    return jsonify({"success": True}), 200


@blueprint.route("/users/<user_id>/notifications", methods=["GET"])
@login_required
def get_notifications(user_id):
    if session["user"] != str(user_id):
        abort(403)

    return jsonify(get_notifications_with_items()), 200


@blueprint.route("/users/<user_id>/notifications", methods=["DELETE"])
@login_required
def delete_all(user_id):
    """Deletes all notification by given user id"""
    if session["user"] != str(user_id):
        abort(403)

    get_resource_service("notifications").delete_action({"user": ObjectId(user_id)})
    return jsonify({"success": True}), 200


@blueprint.route("/users/<user_id>/notifications/<notification_id>", methods=["DELETE"])
@login_required
def delete_notification(user_id, notification_id):
    """Deletes the notification by given id"""
    if session["user"] != str(user_id):
        abort(403)

    get_resource_service("notifications").delete_action({"_id": notification_id})
    return jsonify({"success": True}), 200


@blueprint.route("/users/<user_id>/approve", methods=["POST"])
@account_manager_or_company_admin_only
def approve_user(user_id):
    users_service = get_resource_service("users")
    user = users_service.find_one(req=None, _id=ObjectId(user_id))
    if not user:
        return NotFound(gettext("User not found"))

    if user.get("is_approved"):
        return jsonify({"error": gettext("User is already approved")}), 403

    users_service.approve_user(user)
    return jsonify({"success": True}), 200
