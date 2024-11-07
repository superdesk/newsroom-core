from typing import Any, TypedDict
import io
import zipfile
from inspect import iscoroutinefunction

from bson import ObjectId
from pydantic import BaseModel, field_validator, Field, AliasChoices
from operator import itemgetter
from werkzeug.utils import secure_filename
from quart_babel import gettext

from superdesk.core.types import Request, Response
from superdesk.core import get_app_config, get_current_app
from superdesk import get_resource_service
from superdesk.flask import render_template, send_file
from superdesk.utc import utcnow

from newsroom.types import (
    UserResourceModel,
    TopicResourceModel,
    CompanyResource,
    DashboardModel,
    SectionEnum,
    CardResourceModel,
    WireItem,
    DashboardCardType,
)
from newsroom.exceptions import AuthorizationError
from newsroom.search.types import NewshubSearchRequest
from newsroom.auth.utils import (
    get_user_from_request,
    get_company_from_request,
    is_valid_session,
    check_user_has_products,
)
from newsroom.auth import auth_rules
from newsroom.users.service import UsersService
from newsroom.cards import get_card_size, get_card_type, CardsResourceService
from newsroom.navigations import get_navigations
from newsroom.products import get_products_by_company
from .filters import WireSearchRequestArgs
from .module import wire_endpoints
from newsroom.wire.utils import update_action_list
from newsroom.decorator import redirect_to_login
from newsroom.topics_folders import get_user_folders, get_company_folders
from newsroom.topics.topics_async import get_user_topics_async
from newsroom.email import get_language_template_name, send_user_email
from newsroom.utils import (
    get_json_or_400,
    parse_dates,
    get_type,
    is_json_request,
    query_resource,
    get_agenda_dates,
    get_location_string,
    get_public_contacts,
    get_links,
    get_items_for_user_action,
)
from newsroom.notifications import push_user_notification, push_notification, save_user_notifications
from newsroom.template_filters import is_admin_or_internal
from newsroom.gettext import get_session_locale
from newsroom.public.views import (
    render_public_dashboard,
    PUBLIC_DASHBOARD_CONFIG_CACHE_KEY,
    PUBLIC_DASHBOARD_CARDS_CACHE_KEY,
    PUBLIC_DASHBOARD_ITEMS_CACHE_KEY,
)

from newsroom.assets import ASSETS_RESOURCE, get_upload
from newsroom.ui_config_async import UiConfigResourceService
from newsroom.users import get_user_profile_data
from newsroom.history_async import HistoryService

from .items import get_items_for_dashboard
from .service import WireSearchServiceAsync

HOME_ITEMS_CACHE_KEY = "home_items"
HOME_EXTERNAL_ITEMS_CACHE_KEY = "home_external_items"


async def set_permissions(wire_item: WireItem, ignore_latest=False):
    try:
        cursor = await WireSearchServiceAsync().get_items_by_id(
            [wire_item.id],
            WireSearchRequestArgs(
                ignore_latest=ignore_latest,
                page_size=0,
            ),
            apply_permissions=True,
        )
        permitted = (await cursor.count()) > 0
    except Exception:
        permitted = False

    set_item_permission(wire_item, permitted)


def set_item_permission(wire_item: WireItem, permitted=True):
    if not wire_item:
        return

    wire_item.user_has_access = permitted
    if not wire_item.user_has_access:
        wire_item.body_text = ""
        wire_item.body_html = ""
        wire_item.renditions = None
        wire_item.associations = None


async def get_view_data() -> dict:
    user = get_user_from_request(None)
    user_dict = user.to_dict()
    company = get_company_from_request(None)
    company_dict = company.to_dict() if company else None

    topics = await get_user_topics_async(user)
    user_folders = await get_user_folders(user, "wire") if user else []
    company_folders = await get_company_folders(company, "wire") if company else []
    products = await get_products_by_company(company_dict, product_type="wire") if company_dict else []
    ui_config_service = UiConfigResourceService()

    check_user_has_products(user, products)

    return {
        "user": user_dict,
        "company": str(company.id) if company else None,
        "topics": [topic.to_dict() for topic in topics if topic.topic_type == "wire"],
        "formats": [
            {"format": f["format"], "name": f["name"], "assets": f["assets"]}
            for f in get_current_app().as_any().download_formatters.values()
            if "wire" in f["types"]
        ],
        "navigations": await get_navigations(user_dict, company_dict, "wire"),
        "products": products,
        "saved_items": await WireSearchServiceAsync().get_current_user_bookmarks_count(),
        "context": "wire",
        "ui_config": await ui_config_service.get_section_config("wire"),
        "groups": get_app_config("WIRE_GROUPS", []),
        "user_folders": user_folders,
        "company_folders": company_folders,
        "date_filters": get_app_config("WIRE_TIME_FILTERS", []),
    }


async def get_items_by_card(cards: list[CardResourceModel], company_id: ObjectId | None):
    cache_key = "{}{}".format(HOME_ITEMS_CACHE_KEY, company_id or "")
    app = get_current_app().as_any()
    if app.cache.get(cache_key):
        return app.cache.get(cache_key)

    items_by_card = await get_items_for_dashboard(cards)
    app.cache.set(cache_key, items_by_card, timeout=get_app_config("DASHBOARD_CACHE_TIMEOUT", 300))
    return items_by_card


def delete_dashboard_caches():
    app = get_current_app().as_any()
    app.cache.delete(HOME_ITEMS_CACHE_KEY)
    app.cache.delete(PUBLIC_DASHBOARD_CONFIG_CACHE_KEY)
    app.cache.delete(PUBLIC_DASHBOARD_CARDS_CACHE_KEY)
    app.cache.delete(PUBLIC_DASHBOARD_ITEMS_CACHE_KEY)
    for company in query_resource("companies"):
        app.cache.delete(f"{HOME_ITEMS_CACHE_KEY}{company['_id']}")


class DashboardTopicData(TypedDict):
    _id: str
    items: list[dict[str, Any]]


class DashboardData(TypedDict):
    dashboard_id: str
    dashboard_name: str
    dashboard_card_type: DashboardCardType
    topic_items: list[DashboardTopicData]


async def get_personal_dashboards_data(
    user: UserResourceModel, company: CompanyResource, topics: list[TopicResourceModel]
) -> list[DashboardData]:
    card_type = get_card_type(get_app_config("PERSONAL_DASHBOARD_CARD_TYPE") or "4-picture-text")

    async def get_topic_items(topic: TopicResourceModel):
        try:
            cursor = await WireSearchServiceAsync().search(
                NewshubSearchRequest(
                    args=WireSearchRequestArgs(page_size=get_card_size(card_type)),
                    section=WireSearchServiceAsync.section,
                    current_user=user,
                    user=user,
                    company=company,
                    is_admin=user.is_admin(),
                    topic=topic,
                )
            )
            return await cursor.to_list_raw()
        except AuthorizationError:
            return []

    async def _get_topic_data(topic_id: ObjectId):
        for topic in topics:
            if topic.id == topic_id:
                topic_items = await get_topic_items(topic)
                if topic_items:
                    return {
                        "_id": topic.id,
                        "items": topic_items,
                    }
                break
        return None

    async def _get_dashboard_data(dashboard: DashboardModel, dashboard_index: int):
        return {
            "dashboard_id": f"d{dashboard_index}",
            "dashboard_name": dashboard.name,
            "dashboard_card_type": card_type,
            "topic_items": list(
                filter(None, [await _get_topic_data(topic_id) for topic_id in dashboard.topic_ids or []])
            ),
        }

    dashboards = user.dashboards or []
    return [await _get_dashboard_data(dashboard, i) for i, dashboard in enumerate(dashboards)]


async def get_home_data():
    user = get_user_from_request(None)
    user_dict = user.to_dict()
    company = get_company_from_request(None)
    company_dict = company.to_dict() if company else None

    cards = await (await CardsResourceService().find({"dashboard": "newsroom"})).to_list_raw()
    topics = await get_user_topics_async(user)
    ui_config_service = UiConfigResourceService()

    return {
        "cards": cards,
        "products": await get_products_by_company(company_dict) if company else [],
        "user": str(user.id),
        "userProducts": user_dict.get("products") or [],
        "userType": user.user_type,
        "company": company.id if company else None,
        "companyProducts": company_dict.get("products") if company else [],
        "formats": [
            {
                "format": f["format"],
                "name": f["name"],
                "types": f["types"],
                "assets": f["assets"],
            }
            for f in get_current_app().as_any().download_formatters.values()
        ],
        "context": "wire",
        "topics": [topic.to_dict() for topic in topics],
        "ui_config": await ui_config_service.get_section_config("wire"),
        "groups": get_app_config("WIRE_GROUPS", []),
        "personalizedDashboards": await get_personal_dashboards_data(user, company, topics),
    }


async def get_previous_versions(wire_item: WireItem) -> list[dict]:
    if len(wire_item.ancestors):
        cursor = await WireSearchServiceAsync().get_items_by_id(
            wire_item.ancestors, args=WireSearchRequestArgs(ignore_latest=True)
        )
        ancestors = await cursor.to_list_raw()
        # ancestors = await (await WireSearchServiceAsync().get_items_by_id(wire_item.ancestors)).to_list_raw()
        return sorted(ancestors, key=itemgetter("versioncreated"), reverse=True)
    return []


@wire_endpoints.endpoint("/", auth=False)
async def index():
    if not await is_valid_session():
        data = await render_public_dashboard() if get_app_config("PUBLIC_DASHBOARD") else redirect_to_login()
        return data
    data = await get_home_data()
    user_profile_data = await get_user_profile_data()
    return await render_template("home.html", data=data, user_profile_data=user_profile_data)


class MediaCardRouteArguments(BaseModel):
    card_id: str


@wire_endpoints.endpoint("/media_card_external/<card_id>")
async def get_media_card_external(args: MediaCardRouteArguments, params: None, request: Request) -> Response:
    cache_id = "{}_{}".format(HOME_EXTERNAL_ITEMS_CACHE_KEY, args.card_id)
    app = get_current_app().as_any()

    if app.cache.get(cache_id):
        card_items = app.cache.get(cache_id)
    else:
        card = await CardsResourceService().find_by_id_raw(args.card_id)
        if not card:
            await request.abort(404)
        card_items = app.get_media_cards_external(card)
        app.cache.set(cache_id, card_items, timeout=get_app_config("DASHBOARD_CACHE_TIMEOUT", 300))

    return Response({"_items": card_items})


@wire_endpoints.endpoint("/card_items")
async def get_card_items() -> Response:
    company = get_company_from_request(None)
    cards = await (await CardsResourceService().find({"dashboard": "newsroom"})).to_list()
    items_by_card = await get_items_by_card(cards, company.id if company else None)
    return Response({"_items": items_by_card})


@wire_endpoints.endpoint("/wire", auth=[auth_rules.section_required("wire")])
async def wire() -> str:
    data = await get_view_data()
    user_profile_data = await get_user_profile_data()
    return await render_template("wire_index.html", data=data, user_profile_data=user_profile_data)


@wire_endpoints.endpoint("/bookmarks_wire")
async def bookmarks() -> str:
    data = await get_view_data()
    data["bookmarks"] = True
    user_profile_data = await get_user_profile_data()
    return await render_template("wire_bookmarks.html", data=data, user_profile_data=user_profile_data)


@wire_endpoints.endpoint("/wire/search", auth=[auth_rules.section_required("wire")])
async def search(request: Request) -> Response:
    return await WireSearchServiceAsync().process_web_request(request)


class ItemActionUrlParams(BaseModel):
    type: SectionEnum = SectionEnum.WIRE


@wire_endpoints.endpoint("/download", methods=["POST"])
async def download(args: None, params: ItemActionUrlParams, request: Request):
    """Endpoint to download Wire OR Agenda item(s)"""

    user = get_user_from_request(None)
    data = await request.get_json()
    _format = data.get("format", "text")
    item_type = get_type(data.get("type"))

    if item_type == "agenda":
        # Getting Event and/or Planning items
        # TODO-ASYNC: Update when Agenda is migrated to async
        items = get_items_for_user_action(data["items"], item_type)
    else:
        # Getting Wire items
        cursor = await WireSearchServiceAsync().get_items_for_action(data["items"])
        items = await cursor.to_list_raw()

    _file = io.BytesIO()
    formatter = get_current_app().as_any().download_formatters[_format]["formatter"]
    mimetype = None
    attachment_filename = "%s-newsroom.zip" % utcnow().strftime("%Y%m%d%H%M")
    if formatter.get_mediatype() == "picture":
        if len(items) == 1:
            try:
                picture = formatter.format_item(items[0], item_type=item_type)
                return (
                    await get_upload(picture["media"], filename="baseimage%s" % picture["file_extension"])
                ) or await request.abort(404)
            except ValueError:
                return await request.abort(404)
        else:
            with zipfile.ZipFile(_file, mode="w") as zf:
                for item in items:
                    try:
                        picture = formatter.format_item(item, item_type=item_type)
                        file = get_current_app().media.get(picture["media"], ASSETS_RESOURCE)
                        zf.writestr("baseimage%s" % picture["file_extension"], file.read())
                    except ValueError:
                        pass
            _file.seek(0)
    elif len(items) == 1 or _format == "monitoring":
        item = items[0]
        args_item = item if _format != "monitoring" else items
        parse_dates(item)  # fix for old items

        if iscoroutinefunction(formatter.format_item):
            _file.write(await formatter.format_item(args_item, item_type=item_type))
        else:
            _file.write(formatter.format_item(args_item, item_type=item_type))
        _file.seek(0)
        mimetype = formatter.get_mimetype(item)
        attachment_filename = secure_filename(formatter.format_filename(item))
    elif formatter.MULTI and len(items) != 1:
        # if we have multiple items, so in this case we stored their data in one csv file.
        csv_data, attachment_filename = formatter.format_events(items, item_type=item_type)
        _file.write(csv_data)
        _file.seek(0)
    else:
        with zipfile.ZipFile(_file, mode="w") as zf:
            for item in items:
                if iscoroutinefunction(formatter.format_item):
                    formatted_data = await formatter.format_item(item, item_type=item_type)
                else:
                    formatted_data = formatter.format_item(item, item_type=item_type)

                parse_dates(item)  # fix for old items
                zf.writestr(
                    secure_filename(formatter.format_filename(item)),
                    formatted_data,
                )
        _file.seek(0)

    update_action_list(data["items"], "downloads", force_insert=True)
    await HistoryService().create_history_record(items, "download", user.id, user.company, params.type.value)
    return await send_file(
        _file,
        mimetype=mimetype,
        attachment_filename=attachment_filename,
        as_attachment=True,
    )


@wire_endpoints.endpoint("/wire_share", methods=["POST"])
async def share(args: None, params: ItemActionUrlParams, request: Request) -> Response:
    """Endpoint to share Wire OR Agenda item(s)"""

    current_user = get_user_from_request(None)
    current_user_dict = current_user.to_dict()
    item_type = get_type()
    data = await get_json_or_400()

    assert data.get("users")
    assert data.get("items")

    users_service = UsersService()
    if item_type == "agenda":
        # Getting Event and/or Planning items
        # TODO-ASYNC: Update when Agenda is migrated to async
        items = get_items_for_user_action(data.get("items"), item_type)
    else:
        # Getting Wire items
        cursor = await WireSearchServiceAsync().get_items_for_action(data.get("items"))
        items = await cursor.to_list_raw()

    for user_id in data["users"]:
        user = await users_service.find_by_id(user_id)

        if not user or not user.email:
            continue

        assert user
        user_dict = user.to_dict()

        template_kwargs = {
            "app_name": get_app_config("SITE_NAME"),
            "recipient": user,
            "sender": current_user_dict,
            "items": items,
            "message": data.get("message"),
            "section": params.type,
            "subject_name": items[0].get("headline") or items[0].get("name"),
        }

        if item_type == "agenda":
            template_kwargs["maps"] = data.get("maps") if get_app_config("GOOGLE_MAPS_KEY") else []
            template_kwargs["dateStrings"] = [get_agenda_dates(item) for item in items]
            template_kwargs["locations"] = [get_location_string(item) for item in items]
            template_kwargs["contactList"] = [get_public_contacts(item) for item in items]
            template_kwargs["linkList"] = [get_links(item) for item in items]
            template_kwargs["is_admin"] = is_admin_or_internal(user_dict)

        await save_user_notifications(
            [
                dict(
                    resource=item_type,
                    action="share",
                    user=user.id,
                    item=items[0]["_id"],
                    data=dict(
                        shared_by=dict(
                            _id=current_user.id,
                            first_name=current_user.first_name,
                            last_name=current_user.last_name,
                        ),
                        items=[i["_id"] for i in items],
                    ),
                )
            ]
        )

        await send_user_email(
            user_dict,
            template=f"share_{item_type}",
            template_kwargs=template_kwargs,
        )
    update_action_list(data.get("items"), "shares", item_type=item_type)
    await HistoryService().create_history_record(
        items, "share", current_user.id, current_user.company, params.type.value
    )
    return Response("", 201)


@wire_endpoints.endpoint("/wire", methods=["DELETE"], auth=[auth_rules.admin_only])
async def remove_wire_items(request: Request) -> Response:
    data = await get_json_or_400()
    assert data.get("items")

    wire_service = WireSearchServiceAsync().service

    item_ids = []
    async for item in await wire_service.search({"_id": {"$in": data["items"]}}, use_mongo=True):
        item_ids.append(item.id)
        item_ids.extend(item.ancestors or [])

    if not item_ids:
        await request.abort(404, gettext("Not found"))

    cursor = await wire_service.search({"_id": {"$in": item_ids}}, use_mongo=True)
    async for wire_item in cursor:
        await wire_service.delete(wire_item)

    push_notification("items_deleted", ids=item_ids)
    return Response("")


@wire_endpoints.endpoint("/wire_bookmark", methods=["POST", "DELETE"])
async def bookmark() -> Response:
    """Bookmark an item.

    Stores user id into item.bookmarks array.
    Uses mongodb to update the array and then pushes updated array to elastic.
    """
    data = await get_json_or_400()
    assert data.get("items")
    update_action_list(data.get("items"), "bookmarks", item_type="items")
    push_user_notification("saved_items", count=await WireSearchServiceAsync().get_current_user_bookmarks_count())
    return Response("")


class WireItemRouteArgs(BaseModel):
    item_id: str


@wire_endpoints.endpoint("/wire/<item_id>/copy", methods=["POST"])
async def copy(args: WireItemRouteArgs, params: ItemActionUrlParams, request: Request) -> Response:
    """Endpoint to copy Wire OR Agenda item(s)"""

    item_type = get_type()
    if item_type == "agenda":
        item = get_resource_service("agenda").find_one(req=None, _id=args.item_id)
    else:
        item = (await WireSearchServiceAsync().service.find_by_id(args.item_id)).to_dict()

    if not item:
        await request.abort(404)

    template_filename = "copy_agenda_item" if item_type == "agenda" else "copy_wire_item"
    locale = (get_session_locale() or "en").lower()
    template_name = get_language_template_name(template_filename, locale, "txt")

    template_kwargs = {"item": item}
    if item_type == "agenda":
        template_kwargs.update(
            {
                "location": "" if item_type != "agenda" else get_location_string(item),
                "contacts": get_public_contacts(item),
                "calendars": ", ".join([calendar.get("name") for calendar in item.get("calendars") or []]),
                "user_profile_data": await get_user_profile_data(),
            }
        )
    copy_data = (await render_template(template_name, **template_kwargs)).strip()

    update_action_list([args.item_id], "copies", item_type=item_type)
    user = get_user_from_request(request)
    await HistoryService().create_history_record([item], "copy", user.id, user.company, params.type.value)

    return Response({"data": copy_data})


@wire_endpoints.endpoint("/wire/<item_id>/versions")
async def versions(args: WireItemRouteArgs, params: None, request: Request) -> Response:
    wire_item = await WireSearchServiceAsync().service.find_by_id(args.item_id)
    if wire_item is None:
        await request.abort(404)
    return Response({"_items": await get_previous_versions(wire_item)})


class WireItemUrlParams(BaseModel):
    ignore_latest: bool = Field(validation_alias=AliasChoices("ignore_latest", "ignoreLatest"), default=False)
    print: bool = False
    monitoring_profile: str | None = None
    type: SectionEnum = SectionEnum.WIRE


@wire_endpoints.endpoint("/wire/<item_id>")
async def item(args: WireItemRouteArgs, params: WireItemUrlParams, request: Request) -> Response | str:
    wire_service = WireSearchServiceAsync()

    wire_item = await wire_service.service.find_by_id(args.item_id)
    if not wire_item:
        return await request.abort(404)

    await set_permissions(wire_item, params.ignore_latest)
    ui_config_service = UiConfigResourceService()
    config = await ui_config_service.get_section_config("wire")
    display_char_count = config.get("char_count", False)
    user_profile_data = await get_user_profile_data()
    if is_json_request(request):
        return Response(wire_item)

    if not wire_item.user_has_access:
        return await render_template(
            "wire_item_access_restricted.html", item=wire_item, user_profile_data=user_profile_data
        )

    previous_versions = await get_previous_versions(wire_item)
    template = "wire_item.html"
    data = {"item": wire_item.to_dict()}
    if params.print:
        if params.monitoring_profile:
            # TODO-ASYNC: Figure out what these args are actually, and where are they used (in the template?)
            # data.update(request.view_args)
            template = "monitoring_export.html"
        else:
            template = "wire_item_print.html"

        update_action_list([wire_item.id], "prints", force_insert=True)
        user = get_user_from_request(request)
        await HistoryService().create_history_record(
            [wire_item.to_dict()], "print", user.id, user.company, params.type.value
        )

    return await render_template(
        template,
        **data,
        previous_versions=previous_versions,
        display_char_count=display_char_count,
        user_profile_data=user_profile_data,
    )


class WireItemsRouteArgs(BaseModel):
    item_ids: list[str]

    @field_validator("item_ids", mode="before")
    def parse_item_ids(cls, value: list[str] | str) -> list[str]:
        return [item_id.strip() for item_id in value.split(",")] if isinstance(value, str) else value


@wire_endpoints.endpoint("/wire/items/<item_ids>")
async def items(args: WireItemsRouteArgs, params: WireItemUrlParams, request: Request) -> Response:
    wire_search = WireSearchServiceAsync()

    # First get the items directly from the resource service
    items_cursor = await wire_search.service.search({"bool": {"query": {"must": [{"terms": {"_id": args.item_ids}}]}}})
    if not await items_cursor.count():
        return Response([])

    # Now get the list of items this user has permissions for
    allowed_items_cursor = await wire_search.get_items_by_id(
        args.item_ids, WireSearchRequestArgs(ignore_latest=params.ignore_latest)
    )
    allowed_ids = {item.id async for item in allowed_items_cursor}

    # And set the item permissions for each item
    async for item in items_cursor:
        set_item_permission(item, item.id in allowed_ids)

    return Response(await items_cursor.to_list_raw())
