import logging
from eve.render import send_response
from eve.methods.get import get_internal

from superdesk.flask import render_template, jsonify, request

from newsroom.types import SectionEnum
from newsroom.auth.utils import get_user_from_request, get_company_from_request
from newsroom.formatters import get_formatters_id_and_names
from newsroom.media_releases import blueprint
from newsroom.decorator import login_required, section
from .search import MediaReleasesSearchServiceAsync
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
        "saved_items": await MediaReleasesSearchServiceAsync().get_current_user_bookmarks_count(),
        "context": "media_releases",
        "ui_config": await ui_config_service.get_section_config("media_releases"),
    }


@blueprint.route("/media_releases")
@login_required
@section("media_releases")
async def index():
    data = await get_view_data()
    return await render_template("media_releases_index.html", data=data)


@blueprint.route("/media_releases/search")
@login_required
@section("media_releases")
async def search():
    response = await get_internal("media_releases_search")
    return await send_response("media_releases_search", response)


@blueprint.route("/bookmarks_media_releases")
@login_required
async def bookmarks():
    data = await get_view_data()
    data["bookmarks"] = True
    return await render_template("media_releases_bookmarks.html", data=data)


@blueprint.route("/media_releases_bookmark", methods=["POST", "DELETE"])
@login_required
async def bookmark():
    """Bookmark an item.

    Stores user id into item.bookmarks array.
    Uses mongodb to update the array and then pushes updated array to elastic.
    """
    data = await get_json_or_400()
    assert data.get("items")
    await update_action_list(data.get("items"), "bookmarks", item_type="items")
    push_user_notification(
        "saved_items",
        count=await MediaReleasesSearchServiceAsync().get_current_user_bookmarks_count(),
    )
    return jsonify(), 200


@blueprint.route("/media_releases/<_id>/copy", methods=["POST"])
@login_required
async def copy(_id):
    item_type = get_type()
    get_entity_or_404(_id, item_type)
    await update_action_list([_id], "copies", item_type=item_type)
    return jsonify(), 200


@blueprint.route("/media_releases/<_id>/versions")
@login_required
async def versions(_id):
    item = get_entity_or_404(_id, "items")
    items = get_previous_versions(item)
    return jsonify({"_items": items})


@blueprint.route("/media_releases/<_id>")
@login_required
async def item(_id):
    media_release_service = MediaReleasesSearchServiceAsync()
    media_release_item = await media_release_service.service.find_by_id(_id)
    if not media_release_item:
        await request.abort(404)

    await set_permissions(media_release_item, service=media_release_service)

    ui_config_service = UiConfigResourceService()
    config = await ui_config_service.get_section_config(SectionEnum.MEDIA_RELEASES)
    display_char_count = config.get("char_count", False)
    if is_json_request(request):
        return jsonify(media_release_item.to_dict())
    if not media_release_item.user_has_access:
        return await render_template("wire_item_access_restricted.html", item=media_release_item.to_dict())
    previous_versions = await get_previous_versions(media_release_item)
    if "print" in request.args:
        template = "wire_item_print.html"
        await update_action_list([_id], "prints", force_insert=True)
    else:
        template = "wire_item.html"
    return await render_template(
        template,
        item=media_release_item.to_dict(),
        previous_versions=previous_versions,
        display_char_count=display_char_count,
    )
