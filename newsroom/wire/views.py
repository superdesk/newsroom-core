from typing import Any, TypedDict
import io
import zipfile

from bson import ObjectId
from pydantic import BaseModel, field_validator, Field, AliasChoices
from operator import itemgetter
from werkzeug.utils import secure_filename
from quart_babel import gettext

from superdesk.core.types import Request, Response
from superdesk.core import get_app_config, get_current_app
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
from newsroom.formatters import get_formatters_id_and_names, get_formatter
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

from newsroom.assets import get_upload, get_media_file
from newsroom.ui_config_async import UiConfigResourceService
from newsroom.history_async import HistoryService
from newsroom.wire.formatters.utils import add_media

from .items import get_items_for_dashboard
from .service import WireSearchServiceAsync, WireItemService
from .formatters.picture import PictureFormatter

HOME_ITEMS_CACHE_KEY = "home_items"
HOME_EXTERNAL_ITEMS_CACHE_KEY = "home_external_items"


async def set_permissions(
    wire_item: WireItem, ignore_latest: bool = False, service: WireSearchServiceAsync | None = None
):
    try:
        if not service:
            service = WireSearchServiceAsync()
        cursor = await service.get_items_by_id(
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
    products = await get_products_by_company(company_dict, product_type=SectionEnum.WIRE) if company_dict else []
    ui_config_service = UiConfigResourceService()

    check_user_has_products(user, products)

    return {
        "user": user_dict,
        "company": str(company.id) if company else None,
        "topics": [topic.to_dict() for topic in topics if topic.topic_type == "wire"],
        "formats": get_formatters_id_and_names(SectionEnum.WIRE),
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
                return {
                    "_id": topic.id,
                    "items": await get_topic_items(topic) or [],
                }
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
        "formats": get_formatters_id_and_names(None),
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
        return sorted(ancestors, key=itemgetter("versioncreated"), reverse=True)
    return []


@wire_endpoints.endpoint("/", auth=False)
async def index():
    if not await is_valid_session():
        data = await render_public_dashboard() if get_app_config("PUBLIC_DASHBOARD") else redirect_to_login()
        return data
    data = await get_home_data()
    return await render_template("home.html", data=data)


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
    return await render_template("wire_index.html", data=data)


@wire_endpoints.endpoint("/bookmarks_wire")
async def bookmarks() -> str:
    data = await get_view_data()
    data["bookmarks"] = True
    return await render_template("wire_bookmarks.html", data=data)


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
        from newsroom.agenda import AgendaSearchServiceAsync

        items = await AgendaSearchServiceAsync().get_items_for_action(data["items"])
    else:
        # Getting Wire items
        items = await WireSearchServiceAsync().get_items_for_action(data["items"])

    _file = io.BytesIO()
    formatter = get_formatter(_format)
    mimetype = None
    attachment_filename = "%s-newsroom.zip" % utcnow().strftime("%Y%m%d%H%M")
    if isinstance(formatter, PictureFormatter):
        if len(items) == 1:
            try:
                media_id, file_extension = formatter.get_picture_rendition(items[0], item_type=item_type)
                return (await get_upload(media_id, filename=f"baseimage{file_extension}")) or await request.abort(404)
            except ValueError:
                return await request.abort(404)
        else:
            with zipfile.ZipFile(_file, mode="w") as zf:
                for zip_item in items:
                    try:
                        media_id, file_extension = formatter.get_picture_rendition(zip_item, item_type=item_type)
                        file = await get_media_file(media_id)
                        if not file:
                            return await request.abort(404)
                        zf.writestr(f"baseimage{file_extension}", await file.read())
                    except ValueError:
                        pass
            _file.seek(0)
    elif formatter.MULTI_ZIP:
        with zipfile.ZipFile(_file, mode="w") as zf:
            for zip_item in items:
                parse_dates(zip_item)
                formatted_item = await formatter.format_item(zip_item, item_type=item_type)
                await add_media(zf, zip_item)
                zf.writestr(secure_filename(formatter.format_filename(zip_item)), formatted_item)
        _file.seek(0)
        mimetype = "application/zip"
    elif len(items) == 1:
        parse_dates(items[0])  # fix for old items

        _file.write(await formatter.format_item(items[0], item_type=item_type))
        _file.seek(0)
        mimetype = formatter.MIMETYPE
        if mimetype == "application/json":
            mimetype = "text/plain"
        attachment_filename = secure_filename(formatter.format_filename(items[0]))
    elif len(items) > 1:
        # if we have multiple items, so in this case we stored their data in one csv file.
        file_data, filename = await formatter.format_items(items, item_type=item_type)
        if isinstance(file_data, io.BytesIO):
            _file = file_data
        else:
            _file.write(file_data)
            _file.seek(0)
        mimetype = formatter.BULK_MIMETYPE
        if filename is not None:
            attachment_filename = filename

    await update_action_list(data["items"], "downloads", force_insert=True)
    await HistoryService().create_history_record(items, "download", user.id, user.company, params.type.value)
    return await send_file(
        _file,
        mimetype=mimetype or "text/plain",
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
        from newsroom.agenda import AgendaSearchServiceAsync

        items = await AgendaSearchServiceAsync().get_items_for_action(data.get("items"))
    else:
        # Getting Wire items
        items = await WireSearchServiceAsync().get_items_for_action(data.get("items"))

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

            # Import here to prevent circular imports
            from newsroom.agenda.utils import get_related_events

            template_kwargs["related_events"] = await get_related_events(items[0])

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
    await update_action_list(data.get("items"), "shares", item_type=item_type)
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
    await update_action_list(data.get("items"), "bookmarks", item_type="items")
    push_user_notification("saved_items", count=await WireSearchServiceAsync().get_current_user_bookmarks_count())
    return Response("")


class WireItemRouteArgs(BaseModel):
    item_id: str


@wire_endpoints.endpoint("/wire/<item_id>/copy", methods=["POST"])
async def copy(args: WireItemRouteArgs, params: ItemActionUrlParams, request: Request) -> Response:
    """Endpoint to copy Wire OR Agenda item(s)"""

    from newsroom.agenda import AgendaItemService
    from newsroom.agenda.utils import get_related_events

    # Import here to prevent circular imports
    from newsroom.agenda.utils import remove_fields_for_public_user, remove_restricted_coverage_info

    item_type = get_type()
    service = AgendaItemService() if item_type == "agenda" else WireItemService()
    item_to_copy = (await service.find_by_id(args.item_id)).to_dict()  # type: ignore[attr-defined]
    user = get_user_from_request(request)
    company = get_company_from_request(request)

    if not item_to_copy:
        await request.abort(404)

    template_filename = "copy_agenda_item" if item_type == "agenda" else "copy_wire_item"
    locale = (get_session_locale() or "en").lower()
    template_name = get_language_template_name(template_filename, locale, "txt")

    template_kwargs = {"item": item_to_copy}
    if item_type == "agenda":
        if not is_admin_or_internal(user):
            remove_fields_for_public_user(item_to_copy)

        if company and company.restrict_coverage_info:
            remove_restricted_coverage_info([item_to_copy])

        template_kwargs.update(
            {
                "location": "" if item_type != "agenda" else get_location_string(item_to_copy),
                "contacts": get_public_contacts(item_to_copy),
                "calendars": ", ".join([calendar.get("name") for calendar in item_to_copy.get("calendars") or []]),
                "related_events": await get_related_events(item_to_copy),
            }
        )
    copy_data = (await render_template(template_name, **template_kwargs)).strip()

    await update_action_list([args.item_id], "copies", item_type=item_type)
    await HistoryService().create_history_record([item_to_copy], "copy", user.id, user.company, params.type.value)

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
    format: str | None = None

    @field_validator("print", mode="before")
    def parse_print(cls, value: str | bool | None) -> bool | str | None:
        # Support this URL param as a toggle, if `print` is provided in the URL then it is `True`
        return True if value == "" else value


@wire_endpoints.endpoint("/wire/<item_id>")
async def item(args: WireItemRouteArgs, params: WireItemUrlParams, request: Request, **kwargs) -> Response | str:
    return await item_view_endpoint(args, params, request, **kwargs)


async def item_view_endpoint(
    args: WireItemRouteArgs, params: WireItemUrlParams, request: Request, **kwargs
) -> Response | str:
    wire_service = WireSearchServiceAsync()

    wire_item = await wire_service.service.find_by_id(args.item_id)
    if not wire_item:
        return await request.abort(404)

    await set_permissions(wire_item, params.ignore_latest)
    ui_config_service = UiConfigResourceService()
    config = await ui_config_service.get_section_config("wire")
    display_char_count = config.get("char_count", False)
    if is_json_request(request):
        return Response(wire_item)

    if not wire_item.user_has_access:
        return await render_template("wire_item_access_restricted.html", item=wire_item)

    previous_versions = await get_previous_versions(wire_item)
    template = "wire_item.html"
    data = {"item": wire_item.to_dict()}
    if params.print:
        if params.monitoring_profile:
            data.update(kwargs)
            template = "monitoring_export.html"
        else:
            template = "wire_item_print.html"

        await update_action_list([wire_item.id], "prints", force_insert=True)
        user = get_user_from_request(request)
        await HistoryService().create_history_record(
            [wire_item.to_dict()], "print", user.id, user.company, params.type.value
        )

    return await render_template(
        template,
        **data,
        previous_versions=previous_versions,
        display_char_count=display_char_count,
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
    items_cursor = await wire_search.service.find(
        {"_id": {"$in": args.item_ids}},
        sort=[("versioncreated", -1)],
        use_mongo=True,
    )
    if not await items_cursor.count():
        return Response([])

    # Now get the list of items this user has permissions for
    allowed_items_cursor = await wire_search.get_items_by_id(
        args.item_ids, WireSearchRequestArgs(ignore_latest=params.ignore_latest)
    )
    allowed_ids = {item.id async for item in allowed_items_cursor}

    # And set the item permissions for each item
    response = []
    async for wire_item in items_cursor:
        set_item_permission(wire_item, wire_item.id in allowed_ids)
        response.append(wire_item.to_dict())

    return Response(response)
