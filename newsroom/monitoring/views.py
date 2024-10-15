import base64
from bson import ObjectId

from quart_babel import gettext
from werkzeug.exceptions import NotFound
from eve.methods.get import get_internal
from eve.render import send_response
from newsroom.decorator import admin_only, login_required, account_manager_only, section

from superdesk.core import get_app_config, get_current_app
from superdesk.flask import jsonify, send_file, request, render_template
from superdesk import get_resource_service
from superdesk.logging import logger

from newsroom.auth.utils import get_user_from_request, get_user_id_from_request, get_company_from_request
from newsroom.email import send_user_email
from newsroom.wire.utils import update_action_list
from newsroom.wire.views import item as wire_print
from newsroom.notifications import push_user_notification
from newsroom.wire.search import get_bookmarks_count
from newsroom.monitoring import blueprint
from newsroom.monitoring.utils import (
    get_date_items_dict,
    get_monitoring_file,
    get_items_for_monitoring_report,
)
from newsroom.utils import (
    query_resource,
    find_one,
    get_items_by_id,
    get_entity_or_404,
    get_json_or_400,
    set_original_creator,
    set_version_creator,
    is_json_request,
    get_items_for_user_action,
)

from .forms import MonitoringForm, alert_types
from newsroom.ui_config_async import UiConfigResourceService
from newsroom.users import get_user_profile_data
from newsroom.history_async import HistoryService


async def get_view_data():
    user = get_user_from_request(None)
    company = get_company_from_request(None)
    ui_config_service = UiConfigResourceService()
    return {
        "user": str(user.id),
        "company": str(company.id) if company else None,
        "navigations": get_monitoring_for_company(user.to_dict()),
        "context": "monitoring",
        "groups": get_app_config("MONITORING_GROUPS") or get_app_config("WIRE_GROUPS", []),
        "ui_config": await ui_config_service.get_section_config("monitoring"),
        "saved_items": get_bookmarks_count(user.id, "monitoring"),
        "formats": [
            {"format": f["format"], "name": f["name"]}
            for f in get_current_app().as_any().download_formatters.values()
            if "monitoring" in f["types"]
        ],
        "secondary_formats": [{"format": f[0], "name": f[1]} for f in alert_types],
    }


def get_settings_data():
    return {"companies": list(query_resource("companies", lookup={"sections.monitoring": True}))}


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


def get_monitoring_for_company(user):
    try:
        company = user["company"] if user and user.get("company") else None
        return list(query_resource("monitoring", lookup={"company": company}))
    except KeyError:
        return []


@blueprint.route("/monitoring/<id>/users", methods=["POST"])
@account_manager_only
async def update_users(id):
    updates = await request.get_json()
    if "users" in updates:
        updates["users"] = [ObjectId(u_id) for u_id in updates["users"]]
        get_resource_service("monitoring").patch(id=ObjectId(id), updates=updates)
        return jsonify({"success": True}), 200


@blueprint.route("/monitoring/schedule_companies", methods=["GET"])
@account_manager_only
async def monitoring_companies():
    monitoring_list = list(query_resource("monitoring", lookup={"schedule.interval": {"$ne": None}}))
    companies = get_items_by_id([ObjectId(m["company"]) for m in monitoring_list], "companies")
    return jsonify(companies), 200


@blueprint.route("/monitoring/<id>/schedule", methods=["POST"])
@account_manager_only
async def update_schedule(id):
    updates = await request.get_json()
    get_resource_service("monitoring").patch(id=ObjectId(id), updates=updates)
    return jsonify({"success": True}), 200


@blueprint.route("/monitoring/all", methods=["GET"])
def search_all():
    monitoring_list = list(query_resource("monitoring"))
    return jsonify(monitoring_list), 200


@blueprint.route("/monitoring/search", methods=["GET"])
async def search():
    response = await get_internal("monitoring_search")
    return await send_response("monitoring_search", response)


@blueprint.route("/monitoring/new", methods=["POST"])
@account_manager_only
async def create():
    form = await MonitoringForm.create_form()
    if await form.validate():
        new_data = form.data
        if form.company.data:
            new_data["company"] = ObjectId(form.company.data)
            company_users = list(query_resource("users", lookup={"company": new_data["company"]}))
            new_data["users"] = [ObjectId(u["_id"]) for u in company_users]

        request_updates = await request.get_json()
        process_form_request(new_data, request_updates, form)

        set_original_creator(new_data)
        ids = get_resource_service("monitoring").post([new_data])
        return (
            jsonify({"success": True, "_id": ids[0], "users": new_data.get("users")}),
            201,
        )
    return jsonify(form.errors), 400


@blueprint.route("/monitoring/<_id>", methods=["GET", "POST"])
@login_required
async def edit(_id):
    if request.args.get("context", "") == "wire":
        items = get_items_for_user_action([_id], "items")
        if not items:
            return

        item = items[0]
        if is_json_request(request):
            return jsonify(item)

    if "print" in request.args:
        assert request.args.get("monitoring_profile")
        monitoring_profile = get_entity_or_404(request.args.get("monitoring_profile"), "monitoring")
        items = get_items_for_monitoring_report([_id], monitoring_profile, full_text=True)
        request.view_args["date_items_dict"] = get_date_items_dict(items)
        request.view_args["monitoring_profile"] = monitoring_profile
        request.view_args["monitoring_report_name"] = get_app_config("MONITORING_REPORT_NAME", "Newsroom")
        request.view_args["print"] = True
        return wire_print(_id)

    profile = find_one("monitoring", _id=ObjectId(_id))
    if not profile:
        return NotFound(gettext("monitoring Profile not found"))

    if request.method == "POST":
        form = await MonitoringForm.create_form(monitoring=profile)
        if await form.validate_on_submit():
            updates = form.data
            request_updates = await request.get_json()

            # If the updates have anything other than 'users', only admin or monitoring_admin can update
            if len(request_updates.keys()) == 1 and "users" not in request_updates:
                user = get_user_from_request(None)
                if not user.is_admin():
                    return jsonify({"error": "Bad request"}), 400

                company = get_entity_or_404(profile["company"], "companies")
                if str(user.id) != str(company.get("monitoring_administrator")):
                    return jsonify({"error": "Bad request"}), 400

            process_form_request(updates, request_updates, form)
            set_version_creator(updates)
            get_resource_service("monitoring").patch(ObjectId(_id), updates=updates)
            return jsonify({"success": True}), 200
        return jsonify(form.errors), 400
    return jsonify(profile), 200


@blueprint.route("/monitoring/<_id>", methods=["DELETE"])
@admin_only
async def delete(_id):
    """Deletes the monitoring profile by given id"""
    get_resource_service("monitoring").delete_action({"_id": ObjectId(_id)})
    return jsonify({"success": True}), 200


@blueprint.route("/monitoring")
@section("monitoring")
@login_required
async def index():
    data = await get_view_data()
    user_profile_data = await get_user_profile_data()
    return await render_template("monitoring_index.html", data=data, user_profile_data=user_profile_data)


@blueprint.route("/monitoring/export/<_ids>")
@login_required
async def export(_ids):
    user = get_user_from_request(None)
    _format = request.args.get("format")
    if not _format:
        return jsonify({"message": "No format specified."}), 400

    layout_format = request.args.get("secondary_format")
    formatter = get_current_app().as_any().download_formatters[_format]["formatter"]
    monitoring_profile = get_entity_or_404(request.args.get("monitoring_profile"), "monitoring")
    monitoring_profile["format_type"] = _format
    monitoring_profile["alert_type"] = layout_format
    items = get_items_for_monitoring_report([_id for _id in _ids.split(",")], monitoring_profile)

    if len(items) > 0:
        try:
            _file = await get_monitoring_file(monitoring_profile, items)
        except Exception as e:
            logger.exception(e)
            return jsonify({"message": "Error exporting items to file"}), 400

        if _file:
            update_action_list(_ids.split(","), "export", force_insert=True)
            await HistoryService().create_history_record(items, "export", user.id, user.company, "monitoring")

            return send_file(
                _file,
                mimetype=formatter.get_mimetype(None),
                attachment_filename=formatter.format_filename(None),
                as_attachment=True,
            )

    return jsonify({"message": "No files to export."}), 400


@blueprint.route("/monitoring/share", methods=["POST"])
@login_required
async def share():
    data = await get_json_or_400()
    assert data.get("users")
    assert data.get("items")
    assert data.get("monitoring_profile")
    current_user = get_user_from_request(None)
    monitoring_profile = get_entity_or_404(data.get("monitoring_profile"), "monitoring")
    items = get_items_for_monitoring_report(data.get("items"), monitoring_profile)

    for user_id in data["users"]:
        user = get_resource_service("users").find_one(req=None, _id=user_id)
        template_kwargs = {
            "app_name": get_app_config("SITE_NAME"),
            "profile": monitoring_profile,
            "recipient": user,
            "sender": current_user.to_dict(),
            "message": data.get("message"),
            "item_name": "Monitoring Report",
        }
        formatter = get_current_app().as_any().download_formatters["monitoring_pdf"]["formatter"]
        monitoring_profile["format_type"] = "monitoring_pdf"
        _file = await get_monitoring_file(monitoring_profile, items)
        attachment = base64.b64encode(_file.read())

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

    update_action_list(data.get("items"), "shares")
    await HistoryService().create_history_record(items, "share", current_user.id, current_user.company, "monitoring")
    return jsonify({"success": True}), 200


@blueprint.route("/monitoring_bookmark", methods=["POST", "DELETE"])
@login_required
async def bookmark():
    """Bookmark an item.

    Stores user id into item.bookmarks array.
    Uses mongodb to update the array and then pushes updated array to elastic.
    """
    data = await get_json_or_400()
    assert data.get("items")
    update_action_list(data.get("items"), "bookmarks", item_type="items")
    user_id = get_user_id_from_request(None)
    push_user_notification("saved_items", count=get_bookmarks_count(user_id, "monitoring"))
    return jsonify(), 200


@blueprint.route("/bookmarks_monitoring")
@login_required
async def bookmarks():
    data = await get_view_data()
    data["bookmarks"] = True
    user_profile_data = await get_user_profile_data()
    return await render_template("monitoring_bookmarks.html", data=data, user_profile_data=user_profile_data)
