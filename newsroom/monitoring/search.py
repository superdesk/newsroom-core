from newsroom.types import SectionEnum
from newsroom.wire import WireSearchServiceAsync

from newsroom.wire.filters import apply_highlights
from .filters import MonitoringSearchRequestArgs, default_monitoring_filters, filter_replacements
from newsroom.auth.utils import get_user_or_none_from_request
from newsroom.search.types import NewshubSearchRequest


class MonitoringSearchService(WireSearchServiceAsync):
    search_args_class = MonitoringSearchRequestArgs
    section = SectionEnum.MONITORING
    filters = default_monitoring_filters

    get_topic_items_query_execute_filters = [
        filter_replacements.get(filter_function) or filter_function
        for filter_function in WireSearchServiceAsync.get_topic_items_query_execute_filters
        if filter_function != apply_highlights
    ]

    async def get_current_monitoring_bookmarks_count(self, navigations: list[dict]) -> int:
        """Returns the number of items that have been bookmarked by the current user

        :param section: The section to search for, defaults to ``SectionEnum.WIRE``
        :param navigations: The monitoring profiles defined for the Company
        :returns: The number of items that have been bookmarked by the current user
        """

        user = get_user_or_none_from_request(None)
        if not user:
            return 0

        navigation_ids = [nav.get("_id") for nav in navigations if nav.get("is_enabled")]

        cursor = await self.search(
            NewshubSearchRequest(
                section= self.section,
                args=self.search_args_class(bookmarks=[user.id], page_size=0, navigation_ids=navigation_ids),
            )
        )
        return await cursor.count()
