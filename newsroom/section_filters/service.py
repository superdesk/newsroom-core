from superdesk.core.resources import AsyncCacheableService

from newsroom.types import SectionFilterModel
from newsroom.auth.utils import get_current_request, is_from_request
from newsroom.search.types import BoolQuery
from newsroom.search.service import query_string
from newsroom.core.resources.service import NewshubAsyncResourceService


class SectionFiltersService(NewshubAsyncResourceService[SectionFilterModel], AsyncCacheableService):
    resource_name = "section_filters"
    cache_lookup = {"is_enabled": True}

    async def get_section_filters(self, filter_type: str) -> list[SectionFilterModel]:
        """Get the list of section filter by filter type

        :param filter_type: Type of filter
        """
        section_filters = await self.get_section_filters_dict()
        return section_filters.get(filter_type) or []

    async def get_section_filters_dict(self) -> dict[str, list[SectionFilterModel]]:
        """Get the list of all section filters"""

        request = get_current_request() if is_from_request() else None

        async def get_filters() -> dict[str, list[SectionFilterModel]]:
            filters: dict[str, list[SectionFilterModel]] = {}
            async for f in self.get_all_raw():
                if not f.get("is_enabled"):
                    continue
                elif not filters.get(f.get("filter_type")):
                    filters[f.get("filter_type")] = []
                filters[f.get("filter_type")].append(SectionFilterModel.from_dict(f))
            return filters

        if not request:
            return await get_filters()

        if not request.storage.request.get("section_filters"):
            request.storage.request.set("section_filters", await get_filters())
        return request.storage.request.get("section_filters")

    async def apply_section_filter(
        self, query: BoolQuery, product_type: str, filters: dict[str, list[SectionFilterModel]] | None = None
    ):
        """Get the list of base products for product type

        :param query: Dict of elasticsearch query
        :param product_type: Type of product
        :param filters: filters for each section
        """

        section_filters: list[SectionFilterModel] | None
        if not filters:
            section_filters = await self.get_section_filters(product_type)
        else:
            section_filters = filters.get(product_type)

        if not section_filters:
            return

        for f in section_filters:
            if f.is_enabled and f.query:
                query["bool"].setdefault("filter", []).append(query_string(str(f.query)))
