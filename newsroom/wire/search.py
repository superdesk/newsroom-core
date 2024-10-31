import logging

from eve.utils import ParsedRequest

from superdesk.core import json

from newsroom.types import Section, UserRole
import newsroom
from newsroom.products.products import get_products_by_navigation
from newsroom.search.service import BaseSearchService, SearchQuery


logger = logging.getLogger(__name__)


class WireSearchResource(newsroom.Resource):
    datasource = {
        "search_backend": "elastic",
        "source": "items",
        "projection": {
            "original_id": 1,
            "slugline": 1,
            "headline": 1,
            "body_html": 1,
            "firstcreated": 1,
            "versioncreated": 1,
            "nextversion": 1,
            "ancestors": 1,
            "wordcount": 1,
            "charcount": 1,
            "version": 1,
        },
    }

    item_methods = ["GET"]
    resource_methods = ["GET"]

    allowed_roles = [role for role in UserRole]
    allowed_item_roles = allowed_roles


def items_query(ignore_latest=False):
    query = {
        "bool": {
            "must_not": [{"term": {"type": "composite"}}],
            "filter": [],
        }
    }

    if not ignore_latest:
        query["bool"]["must_not"].append({"constant_score": {"filter": {"exists": {"field": "nextversion"}}}})

    return query


class WireSearchService(BaseSearchService):
    section: Section = "wire"

    # Used by Agenda
    def get_items(self, item_ids, size=None, aggregations=None, apply_permissions=False):
        search = SearchQuery()

        try:
            search.query = {
                "bool": {
                    "must_not": [
                        {"term": {"type": "composite"}},
                    ],
                    "filter": [{"terms": {"_id": item_ids}}],
                    "should": [],
                }
            }

            if apply_permissions:
                self.prefill_search_query(search)
                self.validate_request(search)
                self.apply_filters(search)

            search.source = {
                "query": search.query,
                "size": len(item_ids) if size is None else size,
            }

            if aggregations is not None:
                search.source["aggs"] = aggregations

            req = ParsedRequest()
            req.args = {"source": json.dumps(search.source)}

            return self.internal_get(req, None)

        except Exception as exc:
            logger.error(
                "Error in get_items for query: {}".format(json.dumps(search.source)),
                exc,
                exc_info=True,
            )

    # Used by MarketPlace
    def get_navigation_story_count(self, navigations, section, company, user):
        """Get story count by navigation"""

        search = SearchQuery()
        self.prefill_search_args(search)
        self.prefill_search_items(search)
        search.section = section
        search.user = user
        search.company = company
        self.apply_section_filter(search)

        aggs = {}

        for navigation in navigations:
            navigation_id = navigation.get("_id")
            products = get_products_by_navigation([navigation_id]) or []
            navigation_filter = {"bool": {"should": [], "minimum_should_match": 1}}
            for product in products:
                if product.get("query"):
                    navigation_filter["bool"]["should"].append(self.query_string(product.get("query")))

            if navigation_filter["bool"]["should"]:
                aggs.setdefault("navigations", {}).setdefault("filters", {}).setdefault("filters", {})[
                    str(navigation_id)
                ] = navigation_filter

        source = {"query": search.query, "aggs": aggs, "size": 0}
        req = ParsedRequest()
        req.args = {"source": json.dumps(source)}

        try:
            results = self.internal_get(req, None)
            buckets = results.hits["aggregations"]["navigations"]["buckets"]
            for navigation in navigations:
                navigation_id = navigation.get("_id")
                doc_count = buckets.get(str(navigation_id), {}).get("doc_count", 0)
                if doc_count > 0:
                    navigation["story_count"] = doc_count

        except Exception as exc:
            logger.error(
                "Error in get_navigation_story_count for query: {}".format(json.dumps(source)),
                exc,
                exc_info=True,
            )
