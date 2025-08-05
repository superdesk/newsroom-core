from typing import Any
from datetime import datetime

from superdesk.core.types import ESQuery, RestGetResponse, RestResponseMeta
from superdesk.core.resources import AsyncResourceService
from superdesk.utc import local_to_utc

from newsroom.types import FeaturedResourceModel, SectionEnum
from newsroom.utils import get_local_date
from newsroom.search.types import NewshubSearchRequest
from newsroom.search.utils import query_string_for_section

from .filters import (
    apply_item_state_filter,
    apply_section_filter,
    apply_agenda_filters,
    planning_items_query_string,
    nested_query,
    aggregations,
    AgendaSearchRequestArgs,
)
from .agenda_search import AgendaSearchServiceAsync


class FeaturedService(AsyncResourceService[FeaturedResourceModel]):
    resource_name = "agenda_featured"

    async def on_create(self, docs: list[FeaturedResourceModel]) -> None:
        """
        Add UTC from/to datetimes on save.
        Problem is 31.8. in Sydney is from 30.8. 14:00 UTC to 31.8. 13:59 UTC.
        And because we query later using UTC, we store those UTC datetimes as
        display_from and display_to.
        """
        for item in docs:
            date = datetime.strptime(item.id, "%Y%m%d")
            item.display_from = local_to_utc(item.tz, date.replace(hour=0, minute=0, second=0))
            item.display_to = local_to_utc(item.tz, date.replace(hour=23, minute=59, second=59))
        await super().on_create(docs)

    async def find_one_for_date(self, for_date: datetime) -> FeaturedResourceModel | None:
        return await self.find_one(display_from={"$lte": for_date}, display_to={"$gte": for_date})

    async def get_featured_stories(
        self,
        date_from: str,
        timezone_offset: int = 0,
        query_string: str | None = None,
        filters: dict[str, Any] | None = None,
        from_offset: int = 0,
    ) -> RestGetResponse:
        for_date = datetime.strptime(date_from, "%d/%m/%Y %H:%M")
        local_date = get_local_date(
            for_date.strftime("%Y-%m-%d"),
            for_date.strftime("%H:%M:%S"),
            timezone_offset,
        )
        featured_doc = await self.find_one_for_date(local_date)
        return await self.featured(featured_doc, query_string, filters, from_offset)

    async def featured(
        self,
        featured_doc: FeaturedResourceModel | None = None,
        query_string: str | None = None,
        filters: dict[str, Any] | None = None,
        from_offset: int = 0,
    ) -> RestGetResponse:
        """Return featured items.

        :param Optional[dict] featured_doc: The featured document for the given date
        :param Optional[str] query_string: Optional search query to filter the results
        :param Optional[str] filter_string: Optional filter query to filter the results
        :param int from_offset: Pagination offset for the results
        :return: A list of filtered featured items
        """

        if featured_doc is None or featured_doc.items is None or not len(featured_doc.items):
            return RestGetResponse(
                _items=[],
                _meta=RestResponseMeta(
                    page=from_offset,
                    max_results=0,
                    total=0,
                ),
            )

        def apply_featured_filters(request: NewshubSearchRequest) -> None:
            planning_items_query = nested_query(
                "planning_items",
                {"bool": {"filter": [{"terms": {"planning_items.guid": featured_doc.items}}]}},
                name="featured",
            )

            if query_string:
                request.search.query.filter.append(query_string_for_section(SectionEnum.AGENDA, query_string))
                planning_items_query["nested"]["query"]["bool"]["filter"].append(
                    planning_items_query_string(query_string)
                )

            request.search.query.filter.append(planning_items_query)

        cursor = await AgendaSearchServiceAsync().search(
            NewshubSearchRequest(
                args=AgendaSearchRequestArgs(
                    featured=True,
                    page_size=len(featured_doc.items),
                    page=from_offset,
                    filter=filters,
                ),
                search=ESQuery(aggs=aggregations if not from_offset else {}),
            ),
            filters=[
                apply_item_state_filter,
                apply_section_filter,
                apply_agenda_filters,
                apply_featured_filters,
            ],
        )

        docs_by_id: dict[str, dict[str, Any]] = {}
        for doc in await cursor.to_list_raw():
            for p in doc.get("planning_items") or []:
                docs_by_id[p.get("guid")] = doc

            # Update display dates based on the featured document
            doc.update(
                {
                    "_display_from": featured_doc.display_from,
                    "_display_to": featured_doc.display_to,
                }
            )

        docs = []
        agenda_ids = set()
        for agenda_id in featured_doc.items:
            agenda_item = docs_by_id.get(agenda_id)
            if agenda_item and agenda_item.get("_id") not in agenda_ids:
                docs.append(agenda_item)
                agenda_ids.add(agenda_item.get("_id"))

        response = RestGetResponse(
            _items=docs,
            _meta=RestResponseMeta(
                page=from_offset,
                max_results=len(docs),
                total=len(docs),
            ),
        )
        cursor.extra(response)
        return response
