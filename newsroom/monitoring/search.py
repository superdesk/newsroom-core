from newsroom.types import SectionEnum
from newsroom.wire import WireSearchServiceAsync

from newsroom.wire.filters import apply_highlights
from .filters import MonitoringSearchRequestArgs, default_monitoring_filters, filter_replacements


class MonitoringSearchService(WireSearchServiceAsync):
    search_args_class = MonitoringSearchRequestArgs
    section = SectionEnum.MONITORING
    filters = default_monitoring_filters

    get_topic_items_query_execute_filters = [
        filter_replacements.get(filter_function) or filter_function
        for filter_function in WireSearchServiceAsync.get_topic_items_query_execute_filters
        if filter_function != apply_highlights
    ]
