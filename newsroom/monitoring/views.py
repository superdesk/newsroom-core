import base64

from pydantic import field_validator
from quart_babel import gettext
from werkzeug.exceptions import NotFound

from superdesk.core import get_app_config
from superdesk.core.types import BaseModel, Request, Response
from superdesk.core.resources.fields import ObjectId
from superdesk.flask import send_file, render_template
from superdesk.logging import logger

from newsroom.types import SectionEnum, UserResourceModel
from newsroom.auth import auth_rules
from newsroom.auth.utils import get_user_from_request, get_company_from_request
from newsroom.formatters import get_formatters_id_and_names, get_formatter
from newsroom.email import send_user_email
from newsroom.wire.utils import update_action_list
from newsroom.wire.views import item_view_endpoint as wire_print, WireItemRouteArgs, WireItemUrlParams
from newsroom.notifications import push_user_notification
from newsroom.wire import WireSearchServiceAsync

from newsroom.ui_config_async import UiConfigResourceService
from newsroom.users import UsersService
from newsroom.companies import CompanyServiceAsync
from newsroom.history_async import HistoryService

from .utils import (
    get_date_items_dict,
    get_monitoring_file,
    get_items_for_monitoring_report,
)
from .forms import MonitoringForm, alert_types
from .module import monitoring_endpoints
from .service import MonitoringProfileService
from .search import MonitoringSearchService


async def get_view_data():
    user = get_user_from_request(None)
    company = get_company_from_request(None)
    ui_config_service = UiConfigResourceService()

    return {
        "user": user.to_dict(),
        "company": str(company.id) if company else None,
        "navigations": await get_monitoring_for_company(user),
        "context": "monitoring",
        "groups": get_app_config("MONITORING_GROUPS") or get_app_config("WIRE_GROUPS", []),
        "ui_config": await ui_config_service.get_section_config("monitoring"),
        "saved_items": await MonitoringSearchService().get_current_user_bookmarks_count(),
        "formats": get_formatters_id_and_names(SectionEnum.MONITORING),
        "secondary_formats": [{"format": f[0], "name": f[1]} for f in alert_types],
    }


async def get_settings_data():
    cursor = await CompanyServiceAsync().search({"sections.monitoring": True})
    return {"companies": await cursor.to_list_raw()}


def process_form_request(updates, request_updates, form):
    if "schedule" in request_updates:
        updates["schedule"] = request_updates["schedule"]
        if updates["schedule"].get("interval") == "immediate":
            updates["always_send"] = False

    if "users" in request_updates:
        updates["users"] = [ObjectId(u) for u in request_updates["users"]]

    if form.company.data:
        updates["company"] = ObjectId(form.company.data)

    if "keywords" in request_updates:
        updates["keywords"] = request_updates["keywords"]


async def get_monitoring_for_company(user: UserResourceModel | None):
    company = user.company if user else None
    cursor = await MonitoringProfileService().search({"company": company})
    return await cursor.to_list_raw()


class MonitoringIdUrlArg(BaseModel):
    profile_id: ObjectId


@monitoring_endpoints.endpoint(
    "/monitoring/<string:profile_id>/users", methods=["POST"], auth=[auth_rules.account_manager_only]
)
async def update_users(args: MonitoringIdUrlArg, params: None, request: Request) -> Response:
    updates = await request.get_json()
    if "users" not in updates:
        return Response({"error": gettext("Users data not provided")}, 403)

    updates["users"] = [user_id for user_id in updates["users"]]
    await MonitoringProfileService().update(args.profile_id, updates)
    return Response({"success": True})


@monitoring_endpoints.endpoint(
    "/monitoring/schedule_companies", methods=["GET"], auth=[auth_rules.account_manager_only]
)
async def monitoring_companies() -> Response:
    cursor = await MonitoringProfileService().search({"schedule.interval": {"$ne": None}})
    companies = await CompanyServiceAsync().find_by_ids_raw(
        [monitoring.company async for monitoring in cursor if monitoring.company]
    )

    return Response(companies)


@monitoring_endpoints.endpoint(
    "/monitoring/<string:profile_id>/schedule", methods=["POST"], auth=[auth_rules.account_manager_only]
)
async def update_schedule(args: MonitoringIdUrlArg, params: None, request: Request) -> Response:
    updates = await request.get_json()
    await MonitoringProfileService().update(args.profile_id, updates=updates)
    return Response({"success": True})


@monitoring_endpoints.endpoint("/monitoring/all", methods=["GET"])
async def search_all() -> Response:
    monitoring_list = [monitoring async for monitoring in MonitoringProfileService().get_all_raw()]
    return Response(monitoring_list)


@monitoring_endpoints.endpoint("/monitoring/search", methods=["GET"])
async def search(request: Request) -> Response:
    return await MonitoringSearchService().process_web_request(request)


@monitoring_endpoints.endpoint("/monitoring/new", methods=["POST"], auth=[auth_rules.account_manager_only])
async def create(request: Request) -> Response:
    form = await MonitoringForm.create_form()
    if await form.validate():
        new_data = form.data
        if form.company.data:
            new_data["company"] = ObjectId(form.company.data)
            company_users = await UsersService().search({"company": new_data["company"]})
            new_data["users"] = [user.id async for user in company_users]

        request_updates = await request.get_json()
        process_form_request(new_data, request_updates, form)

        new_items = await MonitoringProfileService().create([new_data])
        return Response({"success": True, "_id": new_items[0].id, "users": new_data.get("users")}, 201)
    return Response(form.errors, 400)


class EditMonitoringUrlParams(WireItemUrlParams):
    context: SectionEnum = SectionEnum.MONITORING

    @field_validator("print", mode="before")
    def parse_print(cls, value: str | bool | None) -> bool | str | None:
        # Support this URL param as a toggle, if `print` is provided in the URL then it is `True`
        return True if value == "" else value


@monitoring_endpoints.endpoint("/monitoring/<string:item_id>", methods=["GET", "POST"])
async def edit(args: WireItemRouteArgs, params: EditMonitoringUrlParams, request: Request) -> Response | str:
    if params.context == SectionEnum.WIRE:
        items = await WireSearchServiceAsync().get_items_for_action([args.item_id])
        if not len(items):
            return Response({"error": gettext("No items found")}, 404)

        item = items[0]
        if request.is_json_request():
            return Response(item)

    if params.print:
        if not params.monitoring_profile:
            return Response({"error": gettext("Monitoring profile ID not provided")}, 400)

        monitoring_profile = await MonitoringProfileService().find_by_id(params.monitoring_profile)
        if not monitoring_profile:
            return Response("", 404)

        items = await get_items_for_monitoring_report([args.item_id], monitoring_profile, full_text=True)

        return await wire_print(
            args,
            params,
            request,
            date_items_dict=get_date_items_dict(items),
            monitoring_profile=monitoring_profile,
            monitoring_report_name=get_app_config("MONITORING_REPORT_NAME", "Newsroom"),
            print=True,
        )

    profile = await MonitoringProfileService().find_by_id(args.item_id)
    if not profile:
        raise NotFound(gettext("monitoring Profile not found"))

    if request.method == "POST":
        form = await MonitoringForm.create_form(monitoring=profile.to_dict())
        if await form.validate_on_submit():
            updates = form.data
            request_updates = await request.get_json()

            # If the updates have anything other than 'users', only admin or monitoring_admin can update
            if len(request_updates.keys()) == 1 and "users" not in request_updates:
                user = get_user_from_request(None)
                if not user.is_admin():
                    return Response({"error": gettext("Bad request")}, 400)

                company = await CompanyServiceAsync().find_by_id(profile["company"])
                if not company:
                    return await request.abort(404)
                if user.id != company.monitoring_administrator:
                    return Response({"error": gettext("Bad request")}, 400)

            process_form_request(updates, request_updates, form)
            updates.pop("id")
            await MonitoringProfileService().update(args.item_id, updates)
            return Response({"success": True})
        return Response(form.errors, 400)
    return Response(profile)


@monitoring_endpoints.endpoint("/monitoring/<string:profile_id>", methods=["DELETE"], auth=[auth_rules.admin_only])
async def delete(args: MonitoringIdUrlArg, params: None, request: Request) -> Response:
    """Deletes the monitoring profile by given id"""
    service = MonitoringProfileService()
    monitoring = await service.find_by_id(args.profile_id)
    if not monitoring:
        return Response({"error": gettext("Item not found")}, 404)
    await MonitoringProfileService().delete(monitoring)
    return Response({"success": True})


@monitoring_endpoints.endpoint("/monitoring", auth=[auth_rules.section_required("monitoring")])
async def index():
    data = await get_view_data()
    return await render_template("monitoring_index.html", data=data)


class ExportMonitoringUrlArgs(BaseModel):
    ids: list[str]

    @field_validator("ids", mode="before")
    def parse_ids(cls, value: list[str] | str) -> list[str]:
        """If value is not a list, then convert it to a list here"""

        return value.split(",") if isinstance(value, str) else value


class ExportMonitoringUrlParams(BaseModel):
    monitoring_profile: ObjectId
    format: str | None = None
    secondary_format: str | None = None


@monitoring_endpoints.endpoint("/monitoring/export/<string:ids>")
async def export(args: ExportMonitoringUrlArgs, params: ExportMonitoringUrlParams, request: Request) -> Response:
    user = get_user_from_request(request)
    if not params.format:
        return Response({"message": gettext("No format specified")}, 400)

    formatter = get_formatter(params.format)
    monitoring_profile = await MonitoringProfileService().find_by_id(params.monitoring_profile)
    if not monitoring_profile:
        return Response({"message": gettext("Monitoring profile not found")}, 404)

    monitoring_profile.format_type = params.format
    monitoring_profile.alert_type = params.secondary_format
    items = await get_items_for_monitoring_report(args.ids, monitoring_profile)

    if len(items) > 0:
        try:
            monitoring_file = await get_monitoring_file(monitoring_profile, items)
        except Exception as e:
            logger.exception(e)
            return Response({"message": gettext("Error exporting items to file")}, 400)

        if monitoring_file:
            await update_action_list(args.ids, "export", force_insert=True)
            await HistoryService().create_history_record(items, "export", user.id, user.company, "monitoring")

            return await send_file(
                monitoring_file,
                mimetype=formatter.MIMETYPE,
                attachment_filename=formatter.format_filename(None),
                as_attachment=True,
            )

    return Response({"message": gettext("No files to export.")}, 400)


@monitoring_endpoints.endpoint("/monitoring/share", methods=["POST"])
async def share(request: Request) -> Response:
    data = await request.get_json()
    if not data:
        return await request.abort(404)

    assert data.get("users")
    assert data.get("items")
    assert data.get("monitoring_profile")
    current_user = get_user_from_request(request)

    monitoring_profile = await MonitoringProfileService().find_by_id(data.get("monitoring_profile"))
    if not monitoring_profile:
        return await request.abort(404)
    items = await get_items_for_monitoring_report(data.get("items"), monitoring_profile)

    users_service = UsersService()
    for user_id in data["users"]:
        user = await users_service.find_by_id_raw(user_id)
        template_kwargs = {
            "app_name": get_app_config("SITE_NAME"),
            "profile": monitoring_profile,
            "recipient": user,
            "sender": current_user.to_dict(),
            "message": data.get("message"),
            "item_name": "Monitoring Report",
        }
        formatter = get_formatter("monitoring_pdf")
        monitoring_profile["format_type"] = "monitoring_pdf"
        monitoring_file = await get_monitoring_file(monitoring_profile, items)
        attachment = base64.b64encode(monitoring_file.read())

        await send_user_email(
            user,
            template="share_items",
            template_kwargs=template_kwargs,
            attachments_info=[
                {
                    "file": attachment,
                    "file_name": formatter.format_filename(None),
                    "content_type": "application/{}".format(formatter.FILE_EXTENSION),
                    "file_desc": "Monitoring Report",
                }
            ],
        )

    await update_action_list(data.get("items"), "shares")
    await HistoryService().create_history_record(items, "share", current_user.id, current_user.company, "monitoring")
    return Response({"success": True})


@monitoring_endpoints.endpoint("/monitoring_bookmark", methods=["POST", "DELETE"])
async def bookmark(request: Request) -> Response:
    """Bookmark an item.

    Stores user id into item.bookmarks array.
    Uses mongodb to update the array and then pushes updated array to elastic.
    """
    data = await request.get_json()
    if not data:
        return await request.abort(404)
    assert data.get("items")
    await update_action_list(data.get("items"), "bookmarks", item_type="items")
    push_user_notification(
        "saved_items",
        count=await WireSearchServiceAsync().get_current_user_bookmarks_count(SectionEnum.MONITORING),
    )
    return Response("")


@monitoring_endpoints.endpoint("/bookmarks_monitoring")
async def bookmarks():
    data = await get_view_data()
    data["bookmarks"] = True
    return await render_template("monitoring_bookmarks.html", data=data)
