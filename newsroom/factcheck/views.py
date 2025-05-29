import logging
from eve.render import send_response
from eve.methods.get import get_internal

from superdesk.flask import render_template, jsonify, request

from newsroom.types import SectionEnum
from newsroom.auth.utils import get_user_from_request, get_company_from_request
from newsroom.formatters import get_formatters_id_and_names
from newsroom.factcheck import blueprint
from newsroom.decorator import login_required, section
from .search import FactCheckSearchServiceAsync
from newsroom.wire.views import (
    update_action_list,
    get_previous_versions,
    set_permissions,
)
from newsroom.utils import get_json_or_400, get_entity_or_404, is_json_request, get_type
from newsroom.notifications import push_user_notification
from newsroom.ui_config_async import UiConfigResourceService

logger = logging.getLogger(__name__)


async def get_view_data():
    """Get the view data"""
    user = get_user_from_request(None)
    company = get_company_from_request(None)
    ui_config_service = UiConfigResourceService()
    return {
        "user": user.to_dict(),
        "company": str(company.id) if company else None,
        "navigations": [],
        "formats": get_formatters_id_and_names(SectionEnum.WIRE),
        "saved_items": await FactCheckSearchServiceAsync().get_current_user_bookmarks_count(),
        "context": "factcheck",
        "ui_config": await ui_config_service.get_section_config("factcheck"),
    }


@blueprint.route("/factcheck")
@login_required
@section("factcheck")
async def index():
    data = await get_view_data()
    return await render_template("factcheck_index.html", data=data)


@blueprint.route("/factcheck/search")
@login_required
@section("factcheck")
async def search():
    response = await get_internal("factcheck_search")
    return await send_response("factcheck_search", response)


@blueprint.route("/bookmarks_factcheck")
@login_required
async def bookmarks():
    data = get_view_data()
    data["bookmarks"] = True
    return await render_template("factcheck_bookmarks.html", data=data)


@blueprint.route("/factcheck_bookmark", methods=["POST", "DELETE"])
@login_required
async def bookmark():
    """Bookmark an item.

    Stores user id into item.bookmarks array.
    Uses mongodb to update the array and then pushes updated array to elastic.
    """
    data = await get_json_or_400()
    assert data.get("items")
    await update_action_list(data.get("items"), "bookmarks", item_type="items")
    push_user_notification("saved_items", count=await FactCheckSearchServiceAsync().get_current_user_bookmarks_count())
    return jsonify(), 200


@blueprint.route("/factcheck/<_id>/copy", methods=["POST"])
@login_required
async def copy(_id):
    item_type = get_type()
    get_entity_or_404(_id, item_type)
    await update_action_list([_id], "copies", item_type=item_type)
    return jsonify(), 200


@blueprint.route("/factcheck/<_id>/versions")
@login_required
async def versions(_id):
    item = get_entity_or_404(_id, "items")
    items = get_previous_versions(item)
    return jsonify({"_items": items})


@blueprint.route("/factcheck/<_id>")
@login_required
async def item(_id):
    factcheck_service = FactCheckSearchServiceAsync()

    factcheck_item = await factcheck_service.service.find_by_id(_id)
    if not factcheck_item:
        await request.abort(404)

    await set_permissions(factcheck_item, service=factcheck_service)

    ui_config_service = UiConfigResourceService()
    config = await ui_config_service.get_section_config(SectionEnum.FACTCHECK)
    display_char_count = config.get("char_count", False)
    if is_json_request(request):
        return jsonify(factcheck_item.to_dict())
    if not factcheck_item.user_has_access:
        return await render_template("wire_item_access_restricted.html", item=factcheck_item.to_dict())
    previous_versions = await get_previous_versions(factcheck_item)
    if "print" in request.args:
        template = "wire_item_print.html"
        await update_action_list([_id], "prints", force_insert=True)
    else:
        template = "wire_item.html"
    return await render_template(
        template,
        item=factcheck_item.to_dict(),
        previous_versions=previous_versions,
        display_char_count=display_char_count,
    )
