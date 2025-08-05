import logging

from eve.utils import ParsedRequest

from superdesk.core import json

from newsroom.types import Section, UserRole
import newsroom
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
    def get_items(self, item_ids, size=None, aggregations=None, apply_permissions=False, sort=None):
        search = SearchQuery()

        try:
            search.query = {
                "bool": {
                    "must": [{"terms": {"_id": item_ids}}],
                    "must_not": [
                        {"term": {"type": "composite"}},
                    ],
                    "filter": [],
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

            if sort:
                search.source["sort"] = sort

            req = ParsedRequest()
            req.args = {"source": json.dumps(search.source)}

            return self.internal_get(req, None)

        except Exception as exc:
            logger.error(
                "Error in get_items for query: {}".format(json.dumps(search.query)),
                exc,
                exc_info=True,
            )
