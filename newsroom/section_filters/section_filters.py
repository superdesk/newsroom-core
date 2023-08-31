import flask
import newsroom
import superdesk

from typing import Dict, List
from newsroom.search.service import query_string


class SectionFiltersResource(newsroom.Resource):
    """
    Section Filters schema
    """

    schema = {
        "name": {"type": "string", "unique": True, "required": True},
        "description": {"type": "string"},
        "sd_product_id": {"type": "string"},
        "query": {"type": "string"},
        "is_enabled": {"type": "boolean", "default": True},
        "filter_type": {"type": "string", "default": "wire"},
        "search_type": {"type": "string", "default": "wire"},
        "original_creator": newsroom.Resource.rel("users"),
        "version_creator": newsroom.Resource.rel("users"),
    }
    datasource = {"source": "section_filters", "default_sort": [("name", 1)]}
    item_methods = ["GET", "PATCH", "DELETE"]
    resource_methods = ["GET", "POST"]
    query_objectid_as_string = True  # needed for companies/navigations lookup to work


class SectionFiltersService(newsroom.Service):
    def get_section_filters(self, filter_type) -> List:
        """Get the list of section filter by filter type

        :param filter_type: Type of filter
        """
        section_filters = self.get_section_filters_dict()
        return section_filters.get(filter_type) or []

    def get_section_filters_dict(self) -> Dict[str, List]:
        """Get the list of all section filters"""
        if not getattr(flask.g, "section_filters", None):
            lookup = {"is_enabled": True}
            section_filters = list(
                superdesk.get_resource_service("section_filters").get_from_mongo(req=None, lookup=lookup)
            )
            filters: Dict[str, List] = {}
            for f in section_filters:
                if not filters.get(f.get("filter_type")):
                    filters[f.get("filter_type")] = []
                filters[f.get("filter_type")].append(f)
            flask.g.section_filters = filters
        return flask.g.section_filters

    def apply_section_filter(self, query, product_type, filters=None):
        """Get the list of base products for product type

        :param query: Dict of elasticsearch query
        :param product_type: Type of product
        :param filters: filters for each section
        """
        if not filters:
            section_filters = self.get_section_filters(product_type)
        else:
            section_filters = filters.get(product_type)

        if not section_filters:
            return

        for f in section_filters:
            if f.get("query"):
                query["bool"]["filter"].append(query_string(f.get("query")))
