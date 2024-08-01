from typing import Dict, Optional
import re

from bson import ObjectId
from datetime import datetime
from flask_babel import gettext
from werkzeug.exceptions import NotFound, BadRequest
from pydantic import BaseModel, ValidationError

from superdesk.core import get_app_config, get_current_app
from superdesk.core.web import Request, Response
from superdesk.core.resources.fields import ObjectId as ObjectIdField
from superdesk.core.resources.validators import get_field_errors_from_pydantic_validation_error
from superdesk import get_resource_service

from newsroom.decorator import admin_only, account_manager_only, login_required
from newsroom.types import AuthProviderConfig
from newsroom.utils import (
    get_public_user_data,
    query_resource,
    get_json_or_400_async,
)
from newsroom.ui_config_async import UiConfigResourceService

from .module import company_endpoints, company_configs
from .companies_async import CompanyService, CompanyResource


def get_company_types_options():
    return [
        dict([(k, v) for k, v in company_type.items() if k in {"id", "name"}])
        for company_type in company_configs.company_types
    ]


async def get_settings_data():
    def render_provider(provider: AuthProviderConfig) -> Dict[str, str]:
        return {
            "_id": provider["_id"],
            "name": str(provider["name"]),
            "auth_type": provider["auth_type"].value,
        }

    ui_config_service = UiConfigResourceService()
    return {
        "companies": [company async for company in CompanyService().get_all_raw()],
        "services": get_app_config("SERVICES"),
        "products": list(query_resource("products")),
        "sections": get_current_app().as_any().sections,
        "company_types": get_company_types_options(),
        "api_enabled": get_app_config("NEWS_API_ENABLED", False),
        "ui_config": await ui_config_service.get_section_config("companies"),
        "countries": get_current_app().as_any().countries,
        "auth_providers": [render_provider(provider) for provider in get_app_config("AUTH_PROVIDERS") or []],
    }


class CompanySearchArgs(BaseModel):
    q: Optional[str] = None


@company_endpoints.endpoint("/companies/search", methods=["GET"])
@account_manager_only
async def search_companies(args: None, params: CompanySearchArgs, request: Request) -> Response:
    lookup = None
    if params.q is not None:
        regex = re.compile(".*{}.*".format(params.q), re.IGNORECASE)
        lookup = {"name": regex}
    cursor = await CompanyService().search(lookup)
    companies = await cursor.to_list_raw()
    return Response(companies, 200, ())


@company_endpoints.endpoint("/companies/new", methods=["POST"])
@account_manager_only
async def create_company(request: Request) -> Response:
    company = await get_json_or_400_async(request)
    if not isinstance(company, dict):
        return request.abort(400)

    company_data = get_company_updates(company)
    company_data["_id"] = ObjectId()

    try:
        new_company = CompanyResource.model_validate(company_data)
        ids = await CompanyService().create([new_company])
    except ValidationError as error:
        return Response(
            {
                field: list(errors.values())[0]
                for field, errors in get_field_errors_from_pydantic_validation_error(error).items()
            },
            400,
            (),
        )

    return Response({"success": True, "_id": ids[0]}, 201, ())


def get_company_updates(data, original=None):
    if original is None:
        original = {}

    updates = {
        "name": data.get("name") or original.get("name"),
        "url": data.get("url") or original.get("url"),
        "sd_subscriber_id": data.get("sd_subscriber_id") or original.get("sd_subscriber_id"),
        "account_manager": data.get("account_manager") or original.get("account_manager"),
        "contact_name": data.get("contact_name") or original.get("contact_name"),
        "contact_email": data.get("contact_email") or original.get("contact_email"),
        "phone": data.get("phone") or original.get("phone"),
        "country": data.get("country") or original.get("country"),
        "is_enabled": data.get("is_enabled", original.get("is_enabled")),
        "company_type": data.get("company_type") or original.get("company_type"),
        "monitoring_administrator": data.get("monitoring_administrator") or original.get("monitoring_administrator"),
        "allowed_ip_list": data.get("allowed_ip_list") or original.get("allowed_ip_list"),
        "auth_domains": data.get("auth_domains"),
        "auth_provider": data.get("auth_provider") or original.get("auth_provider") or "newshub",
        "company_size": data.get("company_size") or original.get("company_size"),
        "referred_by": data.get("referred_by") or original.get("referred_by"),
    }

    # "seats" are not in CompanyResource
    for field in ["sections", "archive_access", "events_only", "restrict_coverage_info", "products", "seats"]:
        if field in data:
            updates[field] = data[field]

    for product in updates.get("products") or []:
        product["_id"] = ObjectId(product["_id"])
        product.setdefault("seats", 0)

    if data.get("expiry_date"):
        updates["expiry_date"] = datetime.strptime(str(data.get("expiry_date"))[:10], "%Y-%m-%d")
    else:
        updates["expiry_date"] = None

    return updates


class CompanyItemArgs(BaseModel):
    company_id: ObjectIdField


@company_endpoints.endpoint("/companies/<string:company_id>", methods=["GET", "POST"])
@account_manager_only
async def edit_company(args: CompanyItemArgs, params: None, request: Request) -> Response:
    service = CompanyService()
    original = await service.find_by_id_raw(args.company_id)

    if not original:
        raise NotFound(gettext("Company not found"))
    elif request.method == "GET":
        return Response(original, 200, ())

    request_json = await get_json_or_400_async(request)
    if not isinstance(request_json, dict):
        return request.abort(400)

    updates = get_company_updates(request_json, original)

    try:
        await service.update(args.company_id, updates)
    except ValidationError as error:
        return Response(
            {
                field: list(errors.values())[0]
                for field, errors in get_field_errors_from_pydantic_validation_error(error).items()
            },
            400,
            (),
        )

    return Response({"success": True}, 200, ())


@company_endpoints.endpoint("/companies/<string:company_id>", methods=["DELETE"])
@admin_only
async def delete_company(args: CompanyItemArgs, params: None, request: Request) -> Response:
    service = CompanyService()
    original = await service.find_by_id(args.company_id)

    if not original:
        raise NotFound(gettext("Company not found"))

    try:
        # TODO-ASYNC: Convert to users async service
        get_resource_service("users").delete_action(lookup={"company": args.company_id})
    except BadRequest as er:
        return Response({"error": str(er)}, 403, ())

    try:
        await service.delete(original)
    except Exception as e:
        return Response({"error": str(e)}, 400, ())

    return Response({"success": True}, 200, ())


@company_endpoints.endpoint("/companies/<string:company_id>/users", methods=["GET"])
@login_required
async def company_users(args: CompanyItemArgs, params: None, request: Request) -> Response:
    # TODO-ASYNC: Convert to users async service
    users = [get_public_user_data(user) for user in query_resource("users", lookup={"company": args.company_id})]
    return Response(users, 200, ())


@company_endpoints.endpoint("/companies/<string:company_id>/approve", methods=["POST"])
@account_manager_only
async def approve_company(args: CompanyItemArgs, params: None, request: Request) -> Response:
    service = CompanyService()
    original = await service.find_by_id(args.company_id)
    if not original:
        raise NotFound(gettext("Company not found"))
    elif original.is_approved:
        return Response({"error": gettext("Company is already approved")}, 403, ())

    # Activate this Company
    updates = {
        "is_enabled": True,
        "is_approved": True,
    }
    await service.update(original.id, updates)

    # Activate the Users of this Company
    # TODO-ASYNC: Convert to users async service
    users_service = get_resource_service("users")
    for user in users_service.get(req=None, lookup={"company": original.id, "is_approved": {"$ne": True}}):
        users_service.approve_user(user)

    return Response({"success": True}, 200, ())
