from datetime import datetime
from eve.utils import ParsedRequest

from newsroom.auth.utils import get_user_from_request, get_company_from_request
from newsroom.agenda.agenda import (
    is_events_only_access,
    _agenda_query,
    nested_query,
    planning_items_query_string,
    aggregations,
    _remove_fields,
    PLANNING_ITEMS_FIELDS,
)
from newsroom.agenda.model import FeaturedResourceModel
from newsroom.core.resources.service import NewshubAsyncResourceService
from newsroom.utils import get_local_date
from newsroom.template_filters import is_admin

from superdesk import get_resource_service
from superdesk.core import json
from superdesk.flask import abort
from superdesk.utc import local_to_utc
from superdesk.utils import ListCursor


class FeaturedService(NewshubAsyncResourceService[FeaturedResourceModel]):
    resource_name = "agenda_featured"

    async def on_create(self, docs):
        """
        Add UTC from/to datetimes on save.

        Problem is 31.8. in Sydney is from 30.8. 14:00 UTC to 31.8. 13:59 UTC.
        And because we query later using UTC, we store those UTC datetimes as
        display_from and display_to.
        """
        for item in docs:
            date = datetime.strptime(item._id, "%Y%m%d")
            item.display_from = local_to_utc(item.tz, date.replace(hour=0, minute=0, second=0))
            item.display_to = local_to_utc(item.tz, date.replace(hour=23, minute=59, second=59))
        await super().on_create(docs)

    async def find_one_for_date(self, for_date: datetime) -> FeaturedResourceModel | None:
        return await self.find_one(req=None, display_from={"$lte": for_date}, display_to={"$gte": for_date})

    async def get_featured_stories(self, req, lookup):
        for_date = datetime.strptime(req.args.get("date_from"), "%d/%m/%Y %H:%M")
        offset = int(req.args.get("timezone_offset", "0"))
        local_date = get_local_date(
            for_date.strftime("%Y-%m-%d"),
            datetime.strftime(for_date, "%H:%M:%S"),
            offset,
        )
        featured_doc = await self.find_one_for_date(local_date)
        return await self.featured(req, lookup, featured_doc)

    async def featured(self, req, lookup, featured):
        """Return featured items.

        :param ParsedRequest req: The parsed in request instance from the endpoint
        :param dict lookup: The parsed in lookup dictionary from the endpoint
        :param dict featured: list featured items
        """
        user = get_user_from_request(None)
        company = get_company_from_request(None)
        if is_events_only_access(user.to_dict(), company.to_dict()):
            abort(403)

        if not featured or not featured.get("items"):
            return ListCursor([])

        query = _agenda_query()
        get_resource_service("section_filters").apply_section_filter(query, self.section)
        planning_items_query = nested_query(
            "planning_items",
            {"bool": {"filter": [{"terms": {"planning_items.guid": featured["items"]}}]}},
            name="featured",
        )
        if req.args.get("q"):
            query["bool"]["filter"].append(self.query_string(req.args["q"]))
            planning_items_query["nested"]["query"]["bool"]["filter"].append(planning_items_query_string(req.args["q"]))

        query["bool"]["filter"].append(planning_items_query)

        source = {"query": query}
        self.set_post_filter(source, req)
        source["size"] = len(featured["items"])
        source["from"] = req.args.get("from", 0, type=int)
        if not source["from"]:
            source["aggs"] = aggregations

        if company and not is_admin(user) and company.get("events_only", False):
            # no adhoc planning items and remove planning items and coverages fields
            query["bool"]["filter"].append({"exists": {"field": "event"}})
            _remove_fields(source, PLANNING_ITEMS_FIELDS)

        internal_req = ParsedRequest()
        internal_req.args = {"source": json.dumps(source)}
        cursor = self.internal_get(internal_req, lookup)

        docs_by_id = {}
        for doc in cursor.docs:
            for p in doc.get("planning_items") or []:
                docs_by_id[p.get("guid")] = doc

            # make the items display on the featured day,
            # it's used in ui instead of dates.start and dates.end
            doc.update(
                {
                    "_display_from": featured["display_from"],
                    "_display_to": featured["display_to"],
                }
            )

        docs = []
        agenda_ids = set()
        for _id in featured["items"]:
            if docs_by_id.get(_id) and docs_by_id.get(_id).get("_id") not in agenda_ids:
                docs.append(docs_by_id.get(_id))
                agenda_ids.add(docs_by_id.get(_id).get("_id"))

        cursor.docs = docs
        return cursor
