import logging

from eve.render import send_response
from eve.methods.get import get_internal

from superdesk.core import get_current_app
from superdesk.flask import render_template, jsonify, request
from newsroom.am_news import blueprint
from newsroom.auth import get_user, get_user_id
from newsroom.decorator import login_required, section
from newsroom.navigations.navigations import get_navigations_by_company
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
    user = get_user()
    ui_config_service = UiConfigResourceService()
    return {
        "user": str(user["_id"]) if user else None,
        "user_type": (user or {}).get("user_type") or "public",
        "company": str(user["company"]) if user and user.get("company") else None,
        "navigations": get_navigations_by_company(
            str(user["company"]) if user and user.get("company") else None,
            product_type="am_news",
        ),
        "formats": [
            {"format": f["format"], "name": f["name"]}
            for f in get_current_app().as_any().download_formatters.values()
            if "wire" in f["types"]
        ],
        "saved_items": get_bookmarks_count(user["_id"], "am_news"),
        "context": "am_news",
        "ui_config": await ui_config_service.get_section_config("am_news"),
    }


@blueprint.route("/am_news")
@login_required
@section("am_news")
async def index():
    data = await get_view_data()
    user_profile_data = await get_user_profile_data()
    return render_template("am_news_index.html", data=data, user_profile_data=user_profile_data)


@blueprint.route("/am_news/search")
@login_required
def search():
    response = get_internal("am_news_search")
    return send_response("am_news_search", response)


@blueprint.route("/bookmarks_am_news")
@login_required
async def bookmarks():
    data = await get_view_data()
    user_profile_data = await get_user_profile_data()
    data["bookmarks"] = True
    return render_template("am_news_bookmarks.html", data=data, user_profile_data=user_profile_data)


@blueprint.route("/am_news_bookmark", methods=["POST", "DELETE"])
@login_required
def bookmark():
    """Bookmark an item.

    Stores user id into item.bookmarks array.
    Uses mongodb to update the array and then pushes updated array to elastic.
    """
    data = get_json_or_400()
    assert data.get("items")
    update_action_list(data.get("items"), "bookmarks", item_type="items")
    user_id = get_user_id()
    push_user_notification("saved_items", count=get_bookmarks_count(user_id, "am_news"))
    return jsonify(), 200


@blueprint.route("/am_news/<_id>/copy", methods=["POST"])
@login_required
def copy(_id):
    item_type = get_type()
    get_entity_or_404(_id, item_type)
    update_action_list([_id], "copies", item_type=item_type)
    return jsonify(), 200


@blueprint.route("/am_news/<_id>/versions")
@login_required
def versions(_id):
    item = get_entity_or_404(_id, "items")
    items = get_previous_versions(item)
    return jsonify({"_items": items})


@blueprint.route("/am_news/<_id>")
@login_required
async def item(_id):
    item = get_entity_or_404(_id, "items")
    user_profile_data = await get_user_profile_data()
    set_permissions(item, "am_news")
    ui_config_service = UiConfigResourceService()
    config = await ui_config_service.get_section_config("am_news")
    display_char_count = config.get("char_count", False)
    if is_json_request(request):
        return jsonify(item)
    if not item.get("_access"):
        return render_template("wire_item_access_restricted.html", item=item, user_profile_data=user_profile_data)
    previous_versions = get_previous_versions(item)
    if "print" in request.args:
        template = "wire_item_print.html"
        update_action_list([_id], "prints", force_insert=True)
    else:
        template = "wire_item.html"
    return render_template(
        template,
        item=item,
        previous_versions=previous_versions,
        display_char_count=display_char_count,
        user_profile_data=user_profile_data,
    )
