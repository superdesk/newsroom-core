import re
import json

from copy import deepcopy
from typing import Any, Dict, Optional
from pydantic import BaseModel, ValidationError, field_validator

from bson import ObjectId
from quart_babel import gettext
from werkzeug.exceptions import BadRequest, NotFound

from superdesk import get_resource_service
from superdesk.core.web import Request, Response
from superdesk.core import get_current_app, get_app_config
from superdesk.core.resources.cursor import SearchRequest
from superdesk.core.resources.fields import ObjectId as ObjectIdField

from newsroom.user_roles import UserRole
from newsroom.auth import get_user_by_email
from newsroom.auth.utils import (
    get_auth_providers,
    send_token,
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
from newsroom.users.forms import UserForm
from newsroom.users.users import (
    COMPANY_ADMIN_ALLOWED_UPDATES,
    COMPANY_ADMIN_ALLOWED_PRODUCT_UPDATES,
    USER_PROFILE_UPDATES,
)
from newsroom.utils import (
    get_json_or_400_async,
    query_resource,
    get_vocabulary,
    response_from_validation,
    success_response,
)
from newsroom.monitoring.views import get_monitoring_for_company
from newsroom.ui_config_async import UiConfigResourceService

from .service import UsersService
from .module import users_endpoints
from .model import UserResourceModel
from .utils import get_company_from_user_or_session, get_user_or_abort, get_company_from_user, add_token_data


class RouteArguments(BaseModel):
    user_id: str


class NotificationRouteArguments(RouteArguments):
    notification_id: str


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

    company_as_dict = None
    if company:
        company_as_dict = company.model_dump(by_alias=True, exclude_unset=True)

    auth_provider = get_company_auth_provider(company_as_dict)
    ui_config_service = UiConfigResourceService()

    user_company = await get_company_from_user(user)

    view_data = {
        "user": user_as_dict,
        "company": getattr(company, "id", ""),
        "topics": get_user_topics(user.id) if user else [],
        "companyName": getattr(user_company, "name", ""),
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
    company: Optional[ObjectIdField] = None
    products_id: Optional[ObjectIdField] = None


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
        sort = str(params.sort)

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
            await request.abort(401)

    mongo_cursor = await UsersService().find(SearchRequest(where=lookup, sort=sort, max_results=250))
    users = await mongo_cursor.to_list_raw()

    return Response(users, 200, ())


@users_endpoints.endpoint("/users/new", methods=["POST"])
@account_manager_or_company_admin_only
async def create(request: Request):
    form = await UserForm.create_form()

    if await form.validate():
        if not _is_email_address_valid(form.email.data):
            return Response({"email": [gettext("Email address is already in use")]}, 400, ())

        creation_data = get_updates_from_form(form, on_create=True)
        creation_data["id"] = ObjectId()

        try:
            new_user = UserResourceModel.model_validate(creation_data)
        except ValidationError as error:
            return response_from_validation(error)

        if is_current_user_company_admin():
            company_from_admin = await get_company_from_user_or_session()
            if not company_from_admin:
                return await request.abort(401)

            # Make sure this new user is associated with ``company`` and as a ``PUBLIC`` user
            new_user.company = company_from_admin.id
            new_user.user_type = UserRole.PUBLIC
        elif form.company.data:
            new_user.company = ObjectId(form.company.data)
        elif new_user.user_type != "administrator":
            return Response({"company": [gettext("Company is required for non administrators")]}, 400, ())

        new_user.receive_email = True
        new_user.receive_app_notifications = True

        company = await get_company_from_user_or_session(new_user)
        if company:
            auth_provider = get_company_auth_provider(company.model_dump(by_alias=True))

            if auth_provider.features["verify_email"]:
                add_token_data(new_user)

        try:
            ids = await UsersService().create([new_user])
        except ValidationError as error:
            return response_from_validation(error)

        if auth_provider.features["verify_email"]:
            user_dict = new_user.model_dump(by_alias=True, exclude_unset=True)
            await send_token(user_dict, token_type="new_account", update_token=False)

        return Response({"success": True, "_id": ids[0]}, 201, ())

    return Response(form.errors, 400, ())


@users_endpoints.endpoint("/users/<string:user_id>/resend_invite", methods=["POST"])
@account_manager_or_company_admin_only
async def resent_invite(args: RouteArguments, params: None, request: Request):
    user = await UsersService().find_by_id(args.user_id)
    company = await get_company_from_user_or_session()
    user_is_company_admin = is_current_user_company_admin()

    user_company = await get_company_from_user_or_session(user)
    if not user_company:
        return await request.abort(403)

    auth_provider = get_company_auth_provider(user_company.model_dump(by_alias=True))

    if not user:
        return NotFound(gettext("User not found"))
    elif user.is_validated:
        return Response({"is_validated": gettext("User is already validated")}, 400, ())
    elif user_is_company_admin and (company is None or user.company != company.id):
        # Company admins can only resent invites for members of their company only
        await request.abort(403)
    elif not auth_provider.features["verify_email"]:
        # Can only regenerate new token if ``verify_email`` is enabled in ``AuthProvider``
        await request.abort(403)

    await send_token(user.model_dump(byalias=True), token_type="new_account")

    return success_response({"success": True})


def _is_email_address_valid(email):
    # TODO-ASYNC: update once `auth` is migrated to async
    existing_user = get_user_by_email(email)
    return not existing_user


@users_endpoints.endpoint("/users/<string:user_id>", methods=["GET", "POST"])
@login_required
async def edit(args: RouteArguments, params: None, request: Request):
    user_is_company_admin = is_current_user_company_admin()
    user_is_admin = is_current_user_admin()
    user_is_account_mgr = is_current_user_account_mgr()
    user_is_non_admin = not (user_is_company_admin or user_is_admin or user_is_account_mgr)

    if not (user_is_admin or user_is_account_mgr or user_is_company_admin) and not is_current_user(args.user_id):
        await request.abort(401)

    user = await UsersService().find_by_id(args.user_id)
    company = await get_company_from_user_or_session()

    if user_is_company_admin and (company is None or user.company != company.id):
        await request.abort(403)

    if not user:
        return NotFound(gettext("User not found"))

    etag = request.get_header("If-Match")
    if etag and user.etag != etag:
        await request.abort(412)

    if request.method == "POST":
        form = await UserForm.create_form()

        if await form.validate_on_submit():
            if form.email.data != user.email and not _is_email_address_valid(form.email.data):
                return Response({"email": [gettext("Email address is already in use")]}, 400, ())

            elif not user_is_company_admin and not form.company.data and form.user_type.data != "administrator":
                return Response({"company": [gettext("Company is required for non administrators")]}, 400, ())

            updates = get_updates_from_form(form)

            if not user_is_admin and updates.get("user_type", "") != (user.user_type or ""):
                await request.abort(401)

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

            try:
                await UsersService().update(args.user_id, updates)
            except ValidationError as error:
                return response_from_validation(error)

            return success_response({"success": True})

        return Response(form.errors, 400, ())

    return success_response(user)


def get_updates_from_form(form: UserForm, on_create=False) -> Dict[str, Any]:
    from newsroom.companies.companies_async import CompanyProduct

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
            CompanyProduct(_id=product["_id"], section=product["product_type"]) for product in products.values()  # type: ignore
        ]

    return updates


@users_endpoints.endpoint("/users/<string:user_id>/profile", methods=["POST"])
@login_required
async def edit_user_profile(args: RouteArguments, params: None, request: Request):
    if not is_current_user(args.user_id):
        await request.abort(403)

    user = await UsersService().find_by_id(args.user_id)
    if not user:
        return NotFound(gettext("User not found"))

    form = await UserForm.create_form(user=user)
    if await form.validate_on_submit():
        updates = {key: val for key, val in form.data.items() if key in USER_PROFILE_UPDATES}
        try:
            await UsersService().update(args.user_id, updates)
        except ValidationError as error:
            return response_from_validation(error)

        return success_response({"success": True})

    return Response(form.errors, 400, ())


@users_endpoints.endpoint("/users/<string:user_id>/notification_schedules", methods=["POST"])
@login_required
async def edit_user_notification_schedules(args: RouteArguments, params: None, request: Request):
    if not is_current_user(args.user_id):
        await request.abort(403)

    user: Optional[UserResourceModel] = await UsersService().find_by_id(args.user_id)
    if not user:
        return NotFound(gettext("User not found"))

    data = await get_json_or_400_async(request)

    updates: Dict[str, Any] = {"notification_schedule": {}}
    if user.notification_schedule:
        user_dict = user.model_dump(by_alias=True)
        updates["notification_schedule"] = deepcopy(user_dict.get("notification_schedule") or {})

    updates["notification_schedule"].update(data)

    try:
        await UsersService().update(args.user_id, updates)
    except ValidationError as error:
        return response_from_validation(error)
    return success_response({"success": True})


@users_endpoints.endpoint("/users/<string:user_id>/validate", methods=["POST"])
@admin_only
async def validate(args: RouteArguments, params: None, request: None):
    return await _resend_token(args.user_id, token_type="validate")


@users_endpoints.endpoint("/users/<string:user_id>/reset_password", methods=["POST"])
@account_manager_or_company_admin_only
async def resend_token(args: RouteArguments, params: None, request: None):
    return await _resend_token(args.user_id, token_type="reset_password")


async def _resend_token(user_id, token_type):
    """
    Sends a new token for a given user_id
    :param user_id: Id of the user to send the token
    :param token_type: validate or reset_password
    :return:
    """
    if not user_id:
        return BadRequest(gettext("User id not provided"))

    user = await UsersService().find_by_id(user_id)
    if not user:
        return NotFound(gettext("User not found"))

    if await send_token(user.model_dump(by_alias=True), token_type):
        return success_response({"success": True})

    return Response({"message": "Token could not be sent"}, 400, ())


@users_endpoints.endpoint("/users/<string:user_id>", methods=["DELETE"])
@account_manager_or_company_admin_only
async def delete(args: RouteArguments, params: None, request: Request):
    """Deletes the user by given id"""
    service = UsersService()
    user = await service.find_by_id(args.user_id)
    await service.delete(user)
    return success_response({"success": True})


@users_endpoints.endpoint("/users/<string:user_id>/notifications", methods=["GET"])
@login_required
async def get_notifications(args: RouteArguments, params: None, request: Request):
    if not is_current_user(args.user_id):
        await request.abort(403)

    # TODO-ASYNC: migrate `get_notifications_with_items` to async
    return success_response(get_notifications_with_items())


@users_endpoints.endpoint("/users/<string:user_id>/notifications", methods=["DELETE"])
@login_required
async def delete_all(args: RouteArguments, params: None, request: Request):
    """Deletes all notification by given user id"""
    if not is_current_user(args.user_id):
        await request.abort(403)

    # TODO-ASYNC: adjust when notifications app is migrated to async
    get_resource_service("notifications").delete_action({"user": ObjectId(args.user_id)})
    return success_response({"success": True})


@users_endpoints.endpoint("/users/<string:user_id>/notifications/<string:notification_id>", methods=["DELETE"])
@login_required
async def delete_notification(args: NotificationRouteArguments, params: None, request: Request):
    """Deletes the notification by given id"""
    if not is_current_user(args.user_id):
        await request.abort(403)

    # TODO-ASYNC: adjust when notifications app is migrated to async
    get_resource_service("notifications").delete_action({"_id": args.notification_id})
    return success_response({"success": True})


@users_endpoints.endpoint("/users/<string:user_id>/approve", methods=["POST"])
@account_manager_or_company_admin_only
async def approve_user(args: RouteArguments, params: None, request: Request):
    users_service = UsersService()
    user = await users_service.find_by_id(args.user_id)
    if not user:
        return NotFound(gettext("User not found"))

    if user.is_approved:
        return Response({"error": gettext("User is already approved")}, 403, ())

    await users_service.approve_user(user)
    return success_response({"success": True})
