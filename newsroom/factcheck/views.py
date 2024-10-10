import logging
from eve.render import send_response
from eve.methods.get import get_internal

from superdesk.core import get_current_app
from superdesk.flask import render_template, jsonify, request

from newsroom.auth.utils import get_user_from_request, get_user_id_from_request, get_company_from_request
from newsroom.factcheck import blueprint
from newsroom.decorator import login_required, section
from newsroom.wire.search import get_bookmarks_count
from newsroom.wire.views import (
    update_action_list,
    get_previous_versions,
    set_permissions,
)
from newsroom.utils import get_json_or_400, get_entity_or_404, is_json_request, get_type
from newsroom.notifications import push_user_notification
from newsroom.ui_config_async import UiConfigResourceService
from newsroom.users import get_user_profile_data

logger = logging.getLogger(__name__)


async def get_view_data():
    """Get the view data"""
    user = get_user_from_request(None)
    company = get_company_from_request(None)
    ui_config_service = UiConfigResourceService()
    return {
        "user": str(user.id),
        "company": str(company.id) if company else None,
        "navigations": [],
        "formats": [
            {"format": f["format"], "name": f["name"]}
            for f in get_current_app().as_any().download_formatters.values()
            if "wire" in f["types"]
        ],
        "saved_items": get_bookmarks_count(user.id, "factcheck"),
        "context": "factcheck",
        "ui_config": await ui_config_service.get_section_config("factcheck"),
    }


@blueprint.route("/factcheck")
@login_required
@section("factcheck")
async def index():
    data = await get_view_data()
    user_profile_data = await get_user_profile_data()
    return await render_template("factcheck_index.html", data=data, user_profile_data=user_profile_data)


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
    user_profile_data = await get_user_profile_data()
    return await render_template("factcheck_bookmarks.html", data=data, user_profile_data=user_profile_data)


@blueprint.route("/factcheck_bookmark", methods=["POST", "DELETE"])
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
    push_user_notification("saved_items", count=get_bookmarks_count(user_id, "factcheck"))
    return jsonify(), 200


@blueprint.route("/factcheck/<_id>/copy", methods=["POST"])
@login_required
async def copy(_id):
    item_type = get_type()
    get_entity_or_404(_id, item_type)
    update_action_list([_id], "copies", item_type=item_type)
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
    user_profile_data = await get_user_profile_data()
    item = get_entity_or_404(_id, "items")
    set_permissions(item, "factcheck")
    ui_config_service = UiConfigResourceService()
    config = await ui_config_service.get_section_config("factcheck")
    display_char_count = config.get("char_count", False)
    if is_json_request(request):
        return jsonify(item)
    if not item.get("_access"):
        return await render_template("wire_item_access_restricted.html", item=item, user_profile_data=user_profile_data)
    previous_versions = get_previous_versions(item)
    if "print" in request.args:
        template = "wire_item_print.html"
        update_action_list([_id], "prints", force_insert=True)
    else:
        template = "wire_item.html"
    return await render_template(
        template,
        item=item,
        previous_versions=previous_versions,
        display_char_count=display_char_count,
        user_profile_data=user_profile_data,
    )
