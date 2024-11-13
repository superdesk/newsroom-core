from newsroom.types import SectionEnum
from newsroom.types.wire import WireItem
from newsroom.wire.service import WireItemService
from newsroom.search.base_service import BaseNewshubSearchService
from newsroom.search.filters import apply_company_filter, apply_section_filter, apply_products_filter

from .filters import (
    apply_date_filter,
    apply_filter_fields,
    apply_projection,
    apply_request_filter,
    prefill_company,
    prefill_products,
    validate_page,
)
from .types import NewsApiSearchRequestArgs


default_search_filters = [
    prefill_company,
    prefill_products,
    apply_section_filter,
    apply_company_filter,
    apply_products_filter,
    apply_filter_fields,
    apply_date_filter,
    apply_request_filter,
    apply_projection,
    validate_page,
]


class NewsApiSearchServiceAsync(BaseNewshubSearchService[NewsApiSearchRequestArgs, WireItem]):
    search_args_class = NewsApiSearchRequestArgs
    filters = default_search_filters
    section = SectionEnum.NEWS_API
    default_sort = [{"versioncreated", 1}]
    default_page_size = 25

    def __init__(self):
        self.service = WireItemService()
