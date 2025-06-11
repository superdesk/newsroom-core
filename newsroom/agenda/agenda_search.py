from typing import Any
from copy import deepcopy
import logging

from superdesk.core.types import Request, Response, SearchRequest, ESQuery

from newsroom.types import (
    AgendaItem,
    AgendaItemType,
    SectionEnum,
    UserResourceModel,
    CompanyResource,
)
from newsroom.auth.utils import get_company_from_request
from newsroom.search.types import NewshubSearchRequest
from newsroom.search.base_web_service import BaseWebSearchService
from newsroom.search.filters import (
    prefill_products,
    apply_products_filter,
    apply_ids_filter,
    apply_advanced_search,
    apply_section_filter,
    apply_company_filter,
)

from .filters import (
    AgendaSearchRequestArgs,
    default_agenda_filters,
    get_date_filters,
    aggregations,
    filters_without_dates,
    prefill_item_type_arg,
    apply_item_state_filter,
    apply_agenda_query_string,
    apply_agenda_filters,
    apply_agenda_date_filters,
)
from .agenda_service import AgendaItemService
from .utils import remove_restricted_coverage_info

logger = logging.getLogger(__name__)


def get_agenda_aggregations(events_only: bool = False):
    aggs = deepcopy(aggregations)
    if events_only:
        aggs.pop("coverage", None)
        aggs.pop("planning_items", None)
        aggs.pop("urgency", None)
        aggs.pop("agendas", None)
    return aggs


class AgendaSearchServiceAsync(BaseWebSearchService[AgendaSearchRequestArgs, AgendaItem]):
    search_args_class = AgendaSearchRequestArgs
    filters = default_agenda_filters
    section = SectionEnum.AGENDA
    default_sort = [("dates.start", 1)]
    default_page_size = 250
    service: AgendaItemService

    get_items_by_id_filters = [
        apply_item_state_filter,
        apply_ids_filter,
    ]
    get_topic_items_query_execute_filters = [
        apply_products_filter,
        apply_agenda_query_string,
        apply_ids_filter,
        apply_agenda_filters,
        apply_advanced_search,
        apply_agenda_date_filters,
    ]
    get_topic_items_query_user_filters = [
        apply_section_filter,
        apply_item_state_filter,
        apply_company_filter,
    ]

    def __init__(self):
        self.service = AgendaItemService()

    async def process_web_request(self, request: Request) -> Response:
        search_request = self.get_search_request_instance(request)
        elastic_query = await self.run_filters_and_return_query(search_request)
        internal_request = SearchRequest(
            sort=search_request.args.sort,
            max_results=search_request.args.page_size,
            page=search_request.args.page,
            aggregations=not search_request.args.page and search_request.args.aggs,
            projection=search_request.args.projection,
            elastic=elastic_query,
        )

        args = search_request.args

        if not args.page and not args.bookmarks and args.aggs:
            internal_request.elastic.aggs = get_agenda_aggregations(
                search_request.args.item_type == AgendaItemType.EVENT
            )

        cursor = await self.service.find(internal_request)
        response, count = await self.get_search_response(internal_request, cursor)

        if args.item_type is None or (args.start_date and args.end_date):
            matching_event_ids: set[str] = (
                set() if args.item_type is not None else await self._get_event_ids_matching_query(args)
            )
            date_range = {} if not (args.start_date and args.end_date) else get_date_filters(args)
            for item in response["_items"]:
                if item["_id"] in matching_event_ids:
                    item["_search_matched_event"] = True
                if date_range:
                    # make the items display on the featured day,
                    # it's used in ui instead of dates.start and dates.end
                    item.update(
                        {
                            "_display_from": date_range.get("gt"),
                            "_display_to": date_range.get("lt"),
                        }
                    )

                await self.service.enhance_item(item)
        else:
            for item in response["_items"]:
                await self.service.enhance_item(item)

        return Response(response, 200, [("X-Total-Count", count)])

    async def _get_event_ids_matching_query(self, args: AgendaSearchRequestArgs) -> set[str]:
        search_request = NewshubSearchRequest[AgendaSearchRequestArgs](
            section=self.section,
            web_request=None,
            args=args.model_copy(),
            search=ESQuery(),
        )
        search_request.args.item_type = AgendaItemType.EVENT
        search_request.args.aggs = False
        search_request.args.projection = {"_id"}

        cursor = await self.search(search_request)
        return set([item["_id"] for item in await cursor.to_list_raw()])

    async def get_saved_items_count(self, user: UserResourceModel, company: CompanyResource | None) -> int:
        def set_user_and_company(request: NewshubSearchRequest) -> None:
            request.current_user = request.user = user
            request.company = company
            request.is_admin = user.is_admin()

        cursor = await self.search(
            AgendaSearchRequestArgs(bookmarks=[user.id], page_size=0),
            filters=[
                set_user_and_company,
                prefill_products,
                prefill_item_type_arg,
            ]
            + filters_without_dates,
        )
        return await cursor.count()

    async def get_items_for_action(self, item_ids: list[str]) -> list[dict[str, Any]]:
        """Searches for item by ID, for use by downloads, sharing etc

        If the current user's company has ``restrict_coverage_info`` config turned on, then
        for each item removes the restricted coverage information

        :param item_ids: A list of item IDs to search for
        :returns: The list of Agenda items
        """

        cursor = await self.get_items_by_id(item_ids)
        items = await cursor.to_list_raw()

        company = get_company_from_request(None)
        if company and company.restrict_coverage_info:
            remove_restricted_coverage_info(items)

        return items
