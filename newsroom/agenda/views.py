from typing import Annotated, Any, cast
from asyncio import gather

from bson import ObjectId
from pydantic import Field, field_validator
from quart_babel import gettext

from superdesk.core import get_app_config
from superdesk.core.types import ESQuery, BaseModel, Request, Response, RestGetResponse
from superdesk.core.resources.cursor import ElasticsearchResourceCursorAsync
from superdesk.flask import render_template

from newsroom.types import AgendaItem, AgendaItemType, SectionEnum
from newsroom.auth import auth_rules
from newsroom.auth.utils import (
    get_user_from_request,
    get_company_from_request,
    check_user_has_products,
)
from newsroom.ui_config_async import UiConfigResourceService
from newsroom.formatters import get_formatters_id_and_names
from newsroom.products import get_products_by_company
from newsroom.topics import get_user_topics_async
from newsroom.topics_folders import get_company_folders, get_user_folders
from newsroom.navigations import get_navigations
from newsroom.notifications import push_user_notification
from newsroom.history_async import HistoryService
from newsroom.search.types import NewshubSearchRequest
from newsroom.search.config import merge_planning_aggs

from newsroom.wire import WireSearchServiceAsync
from newsroom.wire.utils import update_action_list
from newsroom.wire.views import set_item_permission
from newsroom.wire.filters import WireSearchRequestArgs

from newsroom.utils import (
    is_json_request,
    get_json_or_400,
    get_agenda_dates,
    get_location_string,
    get_public_contacts,
    get_links,
    get_vocabulary_async,
    get_groups,
)

from .email import send_coverage_request_email
from .featured_service import FeaturedService
from .utils import remove_fields_for_public_user, remove_restricted_coverage_info, get_related_events
from .module import agenda_endpoints
from .agenda_service import AgendaItemService
from .agenda_search import AgendaSearchServiceAsync
from .filters import AgendaSearchRequestArgs


@agenda_endpoints.endpoint("/agenda", auth=[auth_rules.section_required("agenda")])
async def index() -> str:
    data = await get_view_data()
    return await render_template("agenda_index.html", data=data)


@agenda_endpoints.endpoint("/bookmarks_agenda")
async def bookmarks() -> str:
    data = await get_view_data()
    data["bookmarks"] = True
    return await render_template("agenda_bookmarks.html", data=data)


class AgendaItemViewArgs(BaseModel):
    item_id: Annotated[str, Field(alias="_id")]


class AgendaItemParams(BaseModel):
    print: bool = False
    map: str | None = None
    type: str = "agenda"
    format: str | None = None

    @field_validator("print", mode="before")
    def parse_print(cls, value: str | bool | None) -> bool | str | None:
        # Support this URL param as a toggle, if `print` is provided in the URL then it is `True`
        return True if value == "" else value


@agenda_endpoints.endpoint("/agenda/<_id>")
async def item(args: AgendaItemViewArgs, params: AgendaItemParams, request: Request) -> Response | str:
    agenda_item = await AgendaItemService().find_by_id(args.item_id)
    if not agenda_item:
        await request.abort(404)

    agenda_item_dict = agenda_item.to_dict()
    user = get_user_from_request(None)
    company = get_company_from_request(None)
    if not user.is_admin_or_internal():
        remove_fields_for_public_user(agenda_item_dict)

    if company and not user.is_admin() and company.events_only:
        # if the company has permission events only permission then
        # remove planning items and coverages.
        if not agenda_item_dict.get("event"):
            # for adhoc planning items abort the request
            return await request.abort(403)

        agenda_item_dict.pop("planning_items", None)
        agenda_item_dict.pop("coverages", None)

    if company and company.restrict_coverage_info:
        remove_restricted_coverage_info([agenda_item_dict])

    if is_json_request(request):
        return Response(agenda_item_dict)

    if params.print:
        template = "agenda_item_print.html"
        related_events = await get_related_events(agenda_item_dict)
        await update_action_list([args.item_id], "prints", force_insert=True)
        await HistoryService().create_history_record([agenda_item_dict], "print", user.id, user.company, params.type)
        return await render_template(
            template,
            item=agenda_item_dict,
            map=params.map,
            dateString=get_agenda_dates(agenda_item_dict),
            location=get_location_string(agenda_item_dict),
            contacts=get_public_contacts(agenda_item_dict),
            links=get_links(agenda_item_dict),
            is_admin=user.is_admin_or_internal(),
            related_events=related_events,
        )

    data = await get_view_data()
    data["item"] = agenda_item_dict
    return await render_template(
        "agenda_index.html",
        data=data,
        title=agenda_item_dict.get("name", agenda_item_dict.get("headline")),
    )


@agenda_endpoints.endpoint("/agenda/search", auth=[auth_rules.section_required("agenda")])
async def search(args: None, params: AgendaSearchRequestArgs, request: Request) -> Response:
    user = get_user_from_request(request)
    company = get_company_from_request(None)
    if params.featured:
        if user.is_events_only_access(company):
            return await request.abort(403)
        elif params.start_date is None:
            return await request.abort(400, gettext("No date specified."))

        response = await FeaturedService().get_featured_stories(
            params.start_date,
            params.timezone_offset or 0,
            params.q,
            params.filter,
            params.page or 0,
        )
        return Response(response)

    response = await AgendaSearchServiceAsync().process_web_request(request)
    body: RestGetResponse = response.body

    if len(body.get("_items") or []) and company and company.restrict_coverage_info:
        remove_restricted_coverage_info(body["_items"])

    if body.get("_aggregations"):
        merge_planning_aggs(body["_aggregations"])

    return response


async def get_view_data() -> dict:
    user = get_user_from_request(None)
    user_dict = None if not user else user.to_dict()
    company = get_company_from_request(None)
    company_dict = None if not company else company.to_dict()

    # Helper function to provide an async function, otherwise ``gather`` fails with
    # TypeError('An asyncio.Future, a coroutine or an awaitable is required')
    async def empty_array():
        return []

    (
        topics,
        products,
        navigations,
        ui_config,
        featured_count,
        user_folders,
        company_folders,
        saved_items,
        locators,
    ) = await gather(
        get_user_topics_async(user) if user else empty_array(),
        get_products_by_company(company_dict, product_type=SectionEnum.AGENDA) if company else empty_array(),
        get_navigations(user_dict, company_dict, "agenda"),
        UiConfigResourceService().get_section_config("agenda"),
        FeaturedService().count(),
        get_user_folders(user, "agenda") if user else empty_array(),
        get_company_folders(company, "agenda") if company else empty_array(),
        AgendaSearchServiceAsync().get_saved_items_count(user, company),
        get_vocabulary_async("locators"),
    )

    check_user_has_products(user, products)

    return {
        "user": user_dict or {},
        "company": company.id if company else None,
        "topics": [t.to_dict() for t in topics if t.topic_type == "agenda"],
        "formats": get_formatters_id_and_names(SectionEnum.AGENDA),
        "navigations": navigations,
        "saved_items": saved_items,
        "events_only": company.events_only if company else False,
        "restrict_coverage_info": company.restrict_coverage_info if company else False,
        "locators": locators,
        "ui_config": ui_config,
        "groups": get_groups(get_app_config("AGENDA_GROUPS", []), company_dict),
        "has_agenda_featured_items": featured_count > 0,
        "user_folders": user_folders,
        "company_folders": company_folders,
        "date_filters": get_app_config("AGENDA_TIME_FILTERS", []),
        "location_filters_options": get_app_config("CALENDAR_LOCATIONS_FILTER_OPTIONS", {}),
    }


@agenda_endpoints.endpoint("/agenda/request_coverage", methods=["POST"])
async def request_coverage(request: Request) -> Response:
    user = get_user_from_request(None)
    data = await get_json_or_400()
    assert data.get("item")
    assert data.get("message")
    agenda_item = await AgendaItemService().find_by_id(data.get("item"))
    if not agenda_item:
        return await request.abort(404)
    await send_coverage_request_email(user, data.get("message"), agenda_item)
    return Response("", 201)


@agenda_endpoints.endpoint("/agenda_bookmark", methods=["POST", "DELETE"])
async def bookmark(request: Request) -> Response:
    data = await get_json_or_400()
    assert data.get("items")
    await update_action_list(data.get("items"), "bookmarks", item_type="agenda")
    item_count = await AgendaSearchServiceAsync().get_saved_items_count(
        get_user_from_request(request),
        get_company_from_request(request),
    )
    push_user_notification("saved_items", count=item_count)
    return Response("")


class WatchAgendaParams(BaseModel):
    bookmarks: bool = False


@agenda_endpoints.endpoint("/agenda_watch", methods=["POST", "DELETE"])
async def follow(args: None, params: WatchAgendaParams, request: Request) -> Response:
    data = await get_json_or_400()
    assert data.get("items")
    user = get_user_from_request(request)
    company = get_company_from_request(request)

    agenda_service = AgendaItemService()
    cursor = await agenda_service.search({"_id": {"$in": data.get("items")}}, use_mongo=True)
    agenda_items: dict[str, AgendaItem] = {agenda_item.id: agenda_item async for agenda_item in cursor}

    for item_id in data.get("items"):
        agenda_item = agenda_items.get(item_id)
        if not agenda_item:
            return await request.abort(404)
        coverage_updates = {"coverages": agenda_item.coverages or []}

        for c in coverage_updates["coverages"]:
            if c.watches and user.id in c.watches:
                c.watches.remove(user.id)

        if request.method == "POST":
            updates = {"watches": list(set((agenda_item.watches or []) + [user.id]))}

            if agenda_item.coverages:
                updates.update(coverage_updates)

            await agenda_service.update(agenda_item.id, updates)
        else:
            if params.bookmarks:
                user_item_watches = [user_id for user_id in (agenda_item.watches or []) if user_id == user.id]
                if not user_item_watches:
                    # delete user watches of all coverages
                    await agenda_service.update(agenda_item.id, coverage_updates)
                    return Response("")

            await update_action_list(data.get("items"), "watches", item_type="agenda")

    item_count = await AgendaSearchServiceAsync().get_saved_items_count(user, company)
    push_user_notification("saved_items", count=item_count)
    return Response("")


@agenda_endpoints.endpoint("/agenda_coverage_watch", methods=["POST", "DELETE"])
async def watch_coverage(request: Request) -> Response:
    user = get_user_from_request(request)
    company = get_company_from_request(request)
    data = await get_json_or_400()
    item_id = data.get("item_id")
    assert item_id
    assert data.get("coverage_id")
    agenda_item = await AgendaItemService().find_by_id(item_id)
    if not agenda_item:
        return Response({"error": gettext(f"Agenda item '{item_id}' not found")}, 404)

    body, return_code = await _update_coverage_watch(
        agenda_item, data["coverage_id"], user.id, add=request.method == "POST"
    )
    if return_code == 404:
        return Response(body, 404)

    item_count = await AgendaSearchServiceAsync().get_saved_items_count(user, company)
    push_user_notification("saved_items", count=item_count)
    return Response(body or "", return_code)


async def _update_coverage_watch(
    agenda_item: AgendaItem, coverage_id: str, user_id: ObjectId, add: bool, skip_associated: bool = False
) -> tuple[None, int] | tuple[dict[str, str], int]:
    agenda_service = AgendaItemService()

    if user_id in (agenda_item.watches or []):
        return {"error": gettext("Cannot edit coverage watch when watching parent item")}, 403

    try:
        coverage_index = [c.coverage_id for c in (agenda_item.coverages or [])].index(coverage_id)
    except ValueError:
        return {"error": gettext(f"Coverage '{coverage_id}' not found on agenda item '{agenda_item.id}'")}, 404

    updates = {"coverages": agenda_item.coverages}
    if add:
        updates["coverages"][coverage_index].watches = list(
            set((updates["coverages"][coverage_index].watches or []) + [user_id])
        )
    else:
        try:
            updates["coverages"][coverage_index].watches.remove(user_id)
        except Exception:
            return {"error": gettext("Error removing watch.")}, 404

    await agenda_service.update(agenda_item.id, updates)

    if skip_associated:
        return None, 200
    elif agenda_item.item_type == AgendaItemType.PLANNING and agenda_item.event_id:
        # Need to also update the parent Event's list of coverage watches
        event_item = await agenda_service.find_by_id(agenda_item.event_id)
        if event_item:
            return await _update_coverage_watch(event_item, coverage_id, user_id, add, skip_associated=True)

        # return await _update_coverage_watch(agenda_item.event_id, coverage_id, user_id, add, skip_associated=True)
    elif agenda_item.item_type == AgendaItemType.EVENT:
        # Need to also update the Planning item's list of coverage watches
        planning_item = await agenda_service.find_by_id(agenda_item.coverages[coverage_index].planning_id)
        if planning_item:
            return await _update_coverage_watch(
                planning_item,
                coverage_id,
                user_id,
                add,
                skip_associated=True,
            )

    return None, 200


class RelatedWireUrlArgs(BaseModel):
    wire_id: str


@agenda_endpoints.endpoint("/agenda/wire_items/<wire_id>")
async def related_wire_items(args: RelatedWireUrlArgs, params: None, request: Request) -> Response:
    agenda_service = AgendaItemService()
    query = {"bool": {"filter": [{"term": {"coverages.delivery_id": args.wire_id}}]}}
    cursor = await agenda_service.search({"query": {"nested": {"path": "coverages", "query": query}}})
    agenda_item = await cursor.next_raw()

    if agenda_item is None:
        return Response({"error": gettext("%(section)s item not found", section=get_app_config("AGENDA_SECTION"))}, 404)

    company = get_company_from_request(None)
    if company and company.restrict_coverage_info:
        remove_restricted_coverage_info([agenda_item])

    user = get_user_from_request(None)
    if not user.is_admin_or_internal():
        remove_fields_for_public_user(agenda_item)

    wire_ids = []
    for cov in agenda_item.get("coverages") or []:
        if cov.get("coverage_type") == "text" and cov.get("delivery_id"):
            wire_ids.append(cov["delivery_id"])

    wire_search = WireSearchServiceAsync()
    cursor = await wire_search.service.search({"query": {"bool": {"must": [{"terms": {"_id": wire_ids}}]}}})

    permissioned_result = await wire_search.search(
        NewshubSearchRequest(
            args=WireSearchRequestArgs(
                ids=wire_ids,
                page_size=0,
                aggs=True,
            ),
            search=ESQuery(aggs={"ids": {"terms": {"field": "_id"}}}),
        ),
    )

    buckets = permissioned_result.hits["aggregations"]["ids"]["buckets"]
    permissioned_ids = []
    for b in buckets:
        permissioned_ids.append(b["key"])

    wire_items = []
    async for wire_item in cursor:
        set_item_permission(wire_item, wire_item.id in permissioned_ids)
        wire_items.append(wire_item.to_dict())

    return Response(
        {
            "agenda_item": agenda_item,
            "wire_items": wire_items,
        },
        200,
    )


class SearchLocationsParams(BaseModel):
    q: str = ""


@agenda_endpoints.endpoint("/agenda/search_locations")
async def search_locations(args: None, params: SearchLocationsParams, request: Request) -> Response:
    location_filter_options = get_app_config("CALENDAR_LOCATIONS_FILTER_OPTIONS", {})
    query = params.q
    apply_filters = len(query) > 0

    if apply_filters and not query.startswith("*") and not query.endswith("*"):
        query = f"*{query}*"

    def gen_agg_filter(field: str):
        return {
            "bool": {
                "filter": [
                    {
                        "query_string": {
                            "fields": [f"location.{field}"],
                            "query": query,
                        },
                    }
                ],
            },
        }

    def gen_agg_terms(field: str):
        return {"field": f"location.{field}.keyword", "size": 1000, "exclude": [""]}

    # Start with an empty aggregation structure
    es_query: dict[str, Any] = {"size": 0, "aggs": {}}

    # Exclude agenda items where state is "killed"
    es_query["query"] = {
        "bool": {
            "must_not": [{"term": {"state": "killed"}}],
            "filter": [],
        },
    }

    # Conditionally add aggregations based on configuration
    if location_filter_options.get("city", True):
        es_query["aggs"]["city_search_country"] = {
            "terms": gen_agg_terms("address.country"),
            "aggs": {
                "city_search_state": {
                    "terms": gen_agg_terms("address.state"),
                    "aggs": {
                        "cities": {
                            "terms": gen_agg_terms("address.city"),
                        },
                    },
                },
            },
        }

    if location_filter_options.get("state", True):
        es_query["aggs"]["state_search_country"] = {
            "terms": gen_agg_terms("address.country"),
            "aggs": {
                "states": {
                    "terms": gen_agg_terms("address.state"),
                },
            },
        }

    if location_filter_options.get("country", True):
        es_query["aggs"]["countries"] = {
            "terms": gen_agg_terms("address.country"),
        }

    if location_filter_options.get("place", True):
        es_query["aggs"]["places"] = {"terms": gen_agg_terms("name")}

    if apply_filters:
        es_query["query"] = {
            "bool": {
                "filter": [
                    {
                        "query_string": {
                            "fields": [
                                "location.address.city",
                                "location.address.state",
                                "location.address.country",
                                "location.name",
                            ],
                            "query": query,
                        },
                    }
                ],
            },
        }

        # Conditionally add filtered aggregations based on enabled options
        if location_filter_options.get("city", True):
            es_query["aggs"]["city_search"] = {
                "filter": gen_agg_filter("address.city"),
                "aggs": {"city_search_country": es_query["aggs"].pop("city_search_country")},
            }

        if location_filter_options.get("state", True):
            es_query["aggs"]["state_search"] = {
                "filter": gen_agg_filter("address.state"),
                "aggs": {"state_search_country": es_query["aggs"].pop("state_search_country")},
            }

        if location_filter_options.get("country", True):
            es_query["aggs"]["country_search"] = {
                "filter": gen_agg_filter("address.country"),
                "aggs": {"countries": es_query["aggs"].pop("countries")},
            }

        if location_filter_options.get("place", True):
            es_query["aggs"]["place_search"] = {
                "filter": gen_agg_filter("name"),
                "aggs": {"places": es_query["aggs"].pop("places")},
            }

    cursor = cast(ElasticsearchResourceCursorAsync, await AgendaItemService().search(es_query))
    aggs = cursor.hits.get("aggregations") or {}

    regions = []

    if location_filter_options.get("city", True):
        for country_bucket in (aggs.get("city_search_country") or aggs["city_search"]["city_search_country"])[
            "buckets"
        ]:
            country_name = country_bucket["key"]
            for state_bucket in country_bucket["city_search_state"]["buckets"]:
                state_name = state_bucket["key"]
                for city_bucket in state_bucket["cities"]["buckets"]:
                    regions.append(
                        {"name": city_bucket["key"], "country": country_name, "state": state_name, "type": "city"}
                    )

    if location_filter_options.get("state", True):
        for country_bucket in (aggs.get("state_search_country") or aggs["state_search"]["state_search_country"])[
            "buckets"
        ]:
            country_name = country_bucket["key"]
            for state_bucket in country_bucket["states"]["buckets"]:
                regions.append(
                    {
                        "name": state_bucket["key"],
                        "country": country_name,
                        "type": "state",
                    }
                )

    if location_filter_options.get("country", True):
        for country_bucket in (aggs.get("countries") or aggs["country_search"]["countries"])["buckets"]:
            regions.append(
                {
                    "name": country_bucket["key"],
                    "type": "country",
                }
            )

    places = []
    if location_filter_options.get("place", True):
        places = [bucket["key"] for bucket in (aggs.get("places") or aggs["place_search"]["places"])["buckets"]]

    return Response(
        {
            "regions": regions,
            "places": places,
        }
    )
