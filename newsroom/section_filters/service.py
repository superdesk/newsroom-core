from superdesk.flask import g
from superdesk.core.resources import AsyncCacheableService

from newsroom.types import SectionFilterModel
from newsroom.search import BoolQuery
from newsroom.search.service import query_string
from newsroom.core.resources.service import NewshubAsyncResourceService


class SectionFiltersService(NewshubAsyncResourceService[SectionFilterModel], AsyncCacheableService):
    resource_name = "section_filters"
    cache_lookup = {"is_enabled": True}

    async def get_section_filters(self, filter_type: str) -> list[dict]:
        """Get the list of section filter by filter type

        :param filter_type: Type of filter
        """
        section_filters = await self.get_section_filters_dict()
        return section_filters.get(filter_type) or []

    async def get_section_filters_dict(self) -> dict[str, list[dict]]:
        """Get the list of all section filters"""
        if not getattr(g, "section_filters", None):
            filters: dict[str, list] = {}
            for f in await self.get_cached():
                if not filters.get(f.get("filter_type")):
                    filters[f.get("filter_type")] = []
                filters[f.get("filter_type")].append(f)
            g.section_filters = filters
        return g.section_filters

    async def apply_section_filter(self, query: BoolQuery, product_type: str, filters=None):
        """Get the list of base products for product type

        :param query: Dict of elasticsearch query
        :param product_type: Type of product
        :param filters: filters for each section
        """
        if not filters:
            section_filters = await self.get_section_filters(product_type)
        else:
            section_filters = filters.get(product_type)

        if not section_filters:
            return

        for f in section_filters:
            filter_query = f.get("query")
            if filter_query:
                query["bool"].setdefault("filter", []).append(query_string(str(filter_query)))
