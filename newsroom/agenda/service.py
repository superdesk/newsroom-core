from datetime import datetime
from typing import Optional, Any, List

from newsroom.auth.utils import get_user_from_request, get_company_from_request
from newsroom.agenda.agenda import (
    is_events_only_access,
    build_agenda_query,
    nested_query,
    planning_items_query_string,
    aggregations,
    remove_fields,
    PLANNING_ITEMS_FIELDS,
)
from newsroom.types import FeaturedResourceModel
from newsroom.utils import get_local_date
from newsroom.template_filters import is_admin

from superdesk.flask import abort
from superdesk.core.resources import AsyncResourceService
from superdesk.utc import local_to_utc


class FeaturedService(AsyncResourceService[FeaturedResourceModel]):
    resource_name = "agenda_featured"

    async def on_create(self, docs: List[FeaturedResourceModel]) -> None:
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
        self, date_from: str, timezone_offset: int = 0, query_string: Optional[str] = None, from_offset: int = 0
    ) -> Any:
        for_date = datetime.strptime(date_from, "%d/%m/%Y %H:%M")
        local_date = get_local_date(
            for_date.strftime("%Y-%m-%d"),
            for_date.strftime("%H:%M:%S"),
            timezone_offset,
        )
        featured_doc = await self.find_one_for_date(local_date)
        return await self.featured(featured_doc, query_string, from_offset)

    async def featured(
        self, featured_doc: Optional[dict], query_string: Optional[str] = None, from_offset: int = 0
    ) -> Any:
        """Return featured items.

        :param Optional[dict] featured_doc: The featured document for the given date
        :param Optional[str] query_string: Optional search query to filter the results
        :param int from_offset: Pagination offset for the results
        :return: A list of filtered featured items
        """
        from newsroom.section_filters.service import SectionFiltersService

        user = get_user_from_request(None)
        company = get_company_from_request(None)
        if is_events_only_access(user.to_dict(), company.to_dict()):  # type: ignore
            abort(403)

        if not featured_doc or not featured_doc.get("items"):
            return []

        query = build_agenda_query()
        await SectionFiltersService().apply_section_filter(query, self.section)

        planning_items_query = nested_query(
            "planning_items",
            {"bool": {"filter": [{"terms": {"planning_items.guid": featured_doc["items"]}}]}},
            name="featured",
        )

        if query_string:
            query["bool"]["filter"].append(self.query_string(query_string))
            planning_items_query["nested"]["query"]["bool"]["filter"].append(planning_items_query_string(query_string))

        query["bool"]["filter"].append(planning_items_query)

        source = {"query": query, "size": len(featured_doc["items"]), "from": from_offset}
        # self.set_post_filter(source, req)  # TODO: Confirm usage of function with previous ParsedReq
        if not from_offset:
            source["aggs"] = aggregations

        if company and not is_admin(user) and company.get("events_only", False):
            query["bool"]["filter"].append({"exists": {"field": "event"}})
            remove_fields(source, PLANNING_ITEMS_FIELDS)

        cursor = await self.search(source)

        docs_by_id = {}
        for doc in cursor.docs:
            for p in doc.get("planning_items") or []:
                docs_by_id[p.get("guid")] = doc

            # Update display dates based on the featured document
            doc.update(
                {
                    "_display_from": featured_doc["display_from"],
                    "_display_to": featured_doc["display_to"],
                }
            )

        docs = []
        agenda_ids = set()
        for _id in featured_doc["items"]:
            if docs_by_id.get(_id) and docs_by_id.get(_id).get("_id") not in agenda_ids:  # type: ignore
                docs.append(docs_by_id.get(_id))
                agenda_ids.add(docs_by_id.get(_id).get("_id"))  # type: ignore

        return docs
