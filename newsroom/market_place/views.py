from eve.render import send_response
from eve.methods.get import get_internal

from superdesk.flask import render_template, jsonify, request

from newsroom.types import Navigation, CompanyResource, UserResourceModel, SectionEnum
from newsroom.auth.utils import get_user_from_request, get_company_from_request
from newsroom.formatters import get_formatters_id_and_names
from newsroom.market_place import blueprint, SECTION_ID, SECTION_NAME
from newsroom.decorator import login_required, section
from newsroom.topics import get_user_topics
from newsroom.navigations import get_navigations_by_company
from .search import MarketPlaceSearchServiceAsync
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
)
from newsroom.notifications import push_user_notification
from newsroom.ui_config_async import UiConfigResourceService
from newsroom.cards import CardsResourceService

search_endpoint_name = "{}_search".format(SECTION_ID)


async def get_view_data():
    """Get the view data"""
    user = get_user_from_request(None)
    company = get_company_from_request(None)

    topics = await get_user_topics(user.id)
    navigations = await get_navigations_by_company(
        company.to_dict() if company else None,
        product_type=SECTION_ID,
    )
    await get_story_count(navigations, user, company)
    ui_config_service = UiConfigResourceService()
    return {
        "user": user.to_dict(),
        "user_type": user.user_type,
        "company": str(company.id) if company else None,
        "topics": [t for t in topics if t.get("topic_type") == SECTION_ID],
        "navigations": navigations,
        "formats": get_formatters_id_and_names(SectionEnum.WIRE),
        "saved_items": await MarketPlaceSearchServiceAsync().get_current_user_bookmarks_count(),
        "context": SECTION_ID,
        "ui_config": await ui_config_service.get_section_config(SECTION_ID),
        "home_page": False,
        "title": SECTION_NAME,
    }


async def get_story_count(navigations: list[Navigation], user: UserResourceModel, company: CompanyResource):
    await MarketPlaceSearchServiceAsync().get_navigation_story_count(
        navigations, SectionEnum(SECTION_ID), company, user
    )


async def get_home_page_data():
    """Get home page data for market place"""
    user = get_user_from_request(None)
    company = get_company_from_request(None)

    navigations = await get_navigations_by_company(
        company.to_dict() if company else None,
        product_type=SECTION_ID,
    )
    await get_story_count(navigations, user, company)
    return {
        "user": str(user.id),
        "company": str(company.id) if company else None,
        "navigations": navigations,
        "cards": await (await CardsResourceService().search({"dashboard": SECTION_ID})).to_list_raw(),
        "saved_items": await MarketPlaceSearchServiceAsync().get_current_user_bookmarks_count(),
        "context": SECTION_ID,
        "home_page": True,
        "title": SECTION_NAME,
    }


@blueprint.route("/{}".format(SECTION_ID))
@login_required
@section(SECTION_ID)
async def index():
    data = await get_view_data()
    return await render_template("market_place_index.html", data=data)


@blueprint.route("/{}/home".format(SECTION_ID))
@login_required
@section(SECTION_ID)
async def home():
    return await render_template("market_place_home.html", data=await get_home_page_data())


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
    return await render_template("market_place_bookmarks.html", data=data)


@blueprint.route("/{}_bookmark".format(SECTION_ID), methods=["POST", "DELETE"])
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
        count=await MarketPlaceSearchServiceAsync().get_current_user_bookmarks_count(),
    )
    return jsonify(), 200


@blueprint.route("/{}/<_id>/copy".format(SECTION_ID), methods=["POST"])
@login_required
async def copy(_id):
    item_type = get_type()
    get_entity_or_404(_id, item_type)
    await update_action_list([_id], "copies", item_type=item_type)
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
    marketplace_service = MarketPlaceSearchServiceAsync()
    marketplace_item = await marketplace_service.service.find_by_id(_id)
    if not marketplace_item:
        await request.abort(404)

    await set_permissions(marketplace_item, service=marketplace_service)

    ui_config_service = UiConfigResourceService()
    config = await ui_config_service.get_section_config(SectionEnum.MARKET_PLACE)
    display_char_count = config.get("char_count", False)
    if is_json_request(request):
        return jsonify(marketplace_item.to_dict())
    if not marketplace_item.user_has_access:
        return await render_template("wire_item_access_restricted.html", item=marketplace_item.to_dict())
    previous_versions = await get_previous_versions(marketplace_item)
    if "print" in request.args:
        template = "wire_item_print.html"
        await update_action_list([_id], "prints", force_insert=True)
    else:
        template = "wire_item.html"
    return await render_template(
        template,
        item=marketplace_item.to_dict(),
        previous_versions=previous_versions,
        display_char_count=display_char_count,
    )
