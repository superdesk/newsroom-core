from eve.render import send_response
from eve.methods.get import get_internal

from superdesk.core import get_current_app
from superdesk.flask import render_template, jsonify, request
from superdesk import get_resource_service
from newsroom.market_place import blueprint, SECTION_ID, SECTION_NAME
from newsroom.auth import get_user, get_user_id, get_company_from_user
from newsroom.decorator import login_required, section
from newsroom.topics import get_user_topics
from newsroom.navigations.navigations import get_navigations_by_company
from newsroom.wire.search import get_bookmarks_count
from newsroom.wire.views import (
    update_action_list,
    get_previous_versions,
    set_permissions,
)
from newsroom.utils import (
    get_json_or_400,
    get_entity_or_404,
    is_json_request,
    get_type,
    query_resource,
)
from newsroom.notifications import push_user_notification
from newsroom.ui_config_async import UiConfigResourceService
from newsroom.users import get_user_profile_data


search_endpoint_name = "{}_search".format(SECTION_ID)


async def get_view_data():
    """Get the view data"""
    user = get_user()
    topics = get_user_topics(user["_id"]) if user else []
    navigations = get_navigations_by_company(
        str(user["company"]) if user and user.get("company") else None,
        product_type=SECTION_ID,
    )
    get_story_count(navigations, user)
    ui_config_service = UiConfigResourceService()
    return {
        "user": str(user["_id"]) if user else None,
        "user_type": (user or {}).get("user_type") or "public",
        "company": str(user["company"]) if user and user.get("company") else None,
        "topics": [t for t in topics if t.get("topic_type") == SECTION_ID],
        "navigations": navigations,
        "formats": [
            {"format": f["format"], "name": f["name"]}
            for f in get_current_app().as_any().download_formatters.values()
            if "wire" in f["types"]
        ],
        "saved_items": get_bookmarks_count(user["_id"], SECTION_ID),
        "context": SECTION_ID,
        "ui_config": await ui_config_service.get_section_config(SECTION_ID),
        "home_page": False,
        "title": SECTION_NAME,
    }


def get_story_count(navigations, user):
    company = get_company_from_user(user) if user else None
    get_resource_service(search_endpoint_name).get_navigation_story_count(navigations, SECTION_ID, company, user)


def get_home_page_data():
    """Get home page data for market place"""
    user = get_user()
    navigations = get_navigations_by_company(
        str(user["company"]) if user and user.get("company") else None,
        product_type=SECTION_ID,
    )
    get_story_count(navigations, user)
    return {
        "user": str(user["_id"]) if user else None,
        "company": str(user["company"]) if user and user.get("company") else None,
        "navigations": navigations,
        "cards": list(query_resource("cards", lookup={"dashboard": SECTION_ID})),
        "saved_items": get_bookmarks_count(user["_id"], SECTION_ID),
        "context": SECTION_ID,
        "home_page": True,
        "title": SECTION_NAME,
    }


@blueprint.route("/{}".format(SECTION_ID))
@login_required
@section(SECTION_ID)
async def index():
    data = await get_view_data()
    user_profile_data = await get_user_profile_data()
    return await render_template("market_place_index.html", data=data, user_profile_data=user_profile_data)


@blueprint.route("/{}/home".format(SECTION_ID))
@login_required
@section(SECTION_ID)
async def home():
    user_profile_data = await get_user_profile_data()
    return await render_template(
        "market_place_home.html", data=get_home_page_data(), user_profile_data=user_profile_data
    )


@blueprint.route("/{}/search".format(SECTION_ID))
@login_required
async def search():
    response = await get_internal(search_endpoint_name)
    return await send_response(search_endpoint_name, response)


@blueprint.route("/bookmarks_{}".format(SECTION_ID))
@login_required
@section(SECTION_ID)
async def bookmarks():
    data = await get_view_data()
    data["bookmarks"] = True
    user_profile_data = await get_user_profile_data()
    return await render_template("market_place_bookmarks.html", data=data, user_profile_data=user_profile_data)


@blueprint.route("/{}_bookmark".format(SECTION_ID), methods=["POST", "DELETE"])
@login_required
async def bookmark():
    """Bookmark an item.

    Stores user id into item.bookmarks array.
    Uses mongodb to update the array and then pushes updated array to elastic.
    """
    data = await get_json_or_400()
    assert data.get("items")
    update_action_list(data.get("items"), "bookmarks", item_type="items")
    user_id = get_user_id()
    push_user_notification("saved_items", count=get_bookmarks_count(user_id, SECTION_ID))
    return jsonify(), 200


@blueprint.route("/{}/<_id>/copy".format(SECTION_ID), methods=["POST"])
@login_required
async def copy(_id):
    item_type = get_type()
    get_entity_or_404(_id, item_type)
    update_action_list([_id], "copies", item_type=item_type)
    return jsonify(), 200


@blueprint.route("/{}/<_id>/versions".format(SECTION_ID))
@login_required
async def versions(_id):
    item = get_entity_or_404(_id, "items")
    items = get_previous_versions(item)
    return jsonify({"_items": items})


@blueprint.route("/{}/<_id>".format(SECTION_ID))
@login_required
async def item(_id):
    item = get_entity_or_404(_id, "items")
    set_permissions(item, "aapX")
    ui_config_service = UiConfigResourceService()
    config = await ui_config_service.get_section_config(SECTION_ID)
    display_char_count = config.get("char_count", False)
    user_profile_data = await get_user_profile_data()
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
