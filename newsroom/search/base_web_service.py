from typing import Generic, Any
import logging

from bson import ObjectId

from superdesk.core.types import ESQuery, ESBoolQuery, SearchRequest
from superdesk.core.resources.cursor import ElasticsearchResourceCursorAsync

from newsroom.exceptions import AuthorizationError
from newsroom.types import TopicResourceModel, UserResourceModel, CompanyResource
from newsroom.auth.utils import get_user_sections
from newsroom.products import get_products_by_navigation_async

from .base_service import BaseNewshubSearchService, SearchArgsType, SearchItemType
from .filters import prefill_products, validate_request, prefill_args_from_topic
from .types import SearchFilterFunction, NewshubSearchRequest

logger = logging.getLogger(__name__)


class BaseWebSearchService(
    BaseNewshubSearchService[SearchArgsType, SearchItemType], Generic[SearchArgsType, SearchItemType]
):
    get_items_by_id_filters: list[SearchFilterFunction]

    get_topic_items_query_execute_filters: list[SearchFilterFunction]
    get_topic_items_query_user_filters: list[SearchFilterFunction]

    async def get_items_by_id(
        self,
        item_ids: list[str],
        args: SearchArgsType | None = None,
        apply_permissions: bool = False,
    ) -> ElasticsearchResourceCursorAsync[SearchItemType]:
        """Searches for items by ID, optionally applying user/company permissions

        :param item_ids: A list of item IDs to search for
        :param args: Optional set of request arguments to apply
        :param apply_permissions: Whether to apply user/company permissions or not
        :returns: Elasticsearch cursor with the results
        """

        if args is None:
            args = self.search_args_class()

        args.ids = item_ids
        return await self.search(
            args,
            filters=None if apply_permissions else self.get_items_by_id_filters,
        )

    async def get_items_for_action(self, item_ids: list[str]) -> list[dict[str, Any]]:
        """Searches for item by ID, for use by downloads, sharing etc

        For each item, appends the ``anpa_take_key`` to the slugline if defined

        :param item_ids: A list of item IDs to search for
        :returns: The list of WIre items
        """

        raise NotImplementedError()

    async def get_topic_items_query(
        self,
        topic: TopicResourceModel | None,
        user: UserResourceModel | None,
        company: CompanyResource | None,
        query: ESQuery | None = None,
        args: SearchArgsType | None = None,
    ) -> ESQuery | None:
        """Generate an elasticsearch query, based on topic, user and company

        :param topic: An optional Topic to be added to the request args
        :param user: An optional User to be added to the request args
        :param company: An optional Company to be added to the request args
        :param query: An optional Elasticsearch query to start with
        :param args: An optional request args to start with
        :returns: The generated Elasticsearch query, or None if the supplied User does not have permission
        """

        async def prefill_request(request: NewshubSearchRequest):
            if topic:
                request.topic = topic
            if user:
                request.user = request.current_user = user
                request.is_admin = request.user.is_admin()
            else:
                request.is_admin = False

            if company:
                request.company = company

            if user is None and topic is not None and topic.navigation is not None:
                request.products = await get_products_by_navigation_async(topic.navigation)

        search_request = NewshubSearchRequest(
            section=self.section, web_request=None, args=args or self.search_args_class(), search=query or ESQuery()
        )

        prefill_filter_params: list[SearchFilterFunction] = [
            prefill_request,
            prefill_args_from_topic,
        ]
        execute_filters = self.get_topic_items_query_execute_filters.copy()

        if user is not None:
            # If this query is from a User's perspective, then add
            # validation and section/company filters
            prefill_filter_params.extend([prefill_products, validate_request])
            execute_filters.extend(self.get_topic_items_query_user_filters)

        try:
            return await self.run_filters_and_return_query(search_request, prefill_filter_params + execute_filters)
        except AuthorizationError:
            if user and topic:
                logger.info(f"Notification for user:{user.id} and topic:{topic.id} is skipped")
            pass

        return None

    async def get_matching_topics_for_item(
        self,
        item_id: str,
        topics: list[TopicResourceModel],
        users: list[UserResourceModel],
        companies: dict[ObjectId, CompanyResource],
    ) -> set[ObjectId]:
        """Get a set of Topic IDs that match the supplied item

        :param item_id: The ID of the item to match topics against
        :param topics: The list of Topics to match the item against
        :param users: The list of Users to match the item against
        :param companies: The list of Companies to match the item against
        :returns: A set of Topic IDs that the wire item matches
        """

        return await self.get_matching_topics_for_query(
            topics,
            users,
            companies,
            ESQuery(query=ESBoolQuery(must=[{"term": {"_id": item_id}}])),
        )

    async def get_matching_topics_for_query(
        self,
        topics: list[TopicResourceModel],
        users: list[UserResourceModel],
        companies: dict[ObjectId, CompanyResource],
        query: ESQuery | None = None,
    ) -> set[ObjectId]:
        """Get a set of Topic IDs that match the supplied query

        :param topics: The list of Topics to match the item against
        :param users: The list of Users to match the item against
        :param companies: The list of Companies to match the item against
        :param query: The Elasticsearch query to match topics for
        :returns: A set of Topic IDs that the wire item matches
        """

        topic_matches: set[ObjectId] = set()
        topics_checked: set[ObjectId] = set()

        for user in users:
            company = companies.get(user.company) if user.company else None
            user_sections = get_user_sections(user, company)
            if not user_sections.get(self.section):
                continue

            if user.has_paused_notifications():
                continue

            aggs: dict[str, Any] = {"topics": {"filters": {"filters": {}}}}

            # There will be one base search for a user with aggs for user topics
            search = await self.get_topic_items_query(None, user, company, query=query)
            if not search:
                continue

            queried_topics: list[TopicResourceModel] = []
            for topic in topics:
                if topic.user is None or topic.user != user.id:
                    continue
                elif topic.id in topics_checked:
                    continue
                topics_checked.add(topic.id)

                topic_query = await self.get_topic_items_query(topic, None, None)
                if not topic_query:
                    continue

                try:
                    aggs["topics"]["filters"]["filters"][str(topic.id)] = topic_query.generate_query_dict()["query"]
                    queried_topics.append(topic)
                except (KeyError, TypeError, IndexError):
                    continue

            if not len(queried_topics):
                continue

            search.aggs = aggs
            search_request = SearchRequest(
                max_results=0,
                aggregations=True,
                elastic=search,
            )

            try:
                search_results: ElasticsearchResourceCursorAsync[SearchItemType] = await self.service.find(
                    search_request
                )
                for topic in queried_topics:
                    try:
                        if search_results.hits["aggregations"]["topics"]["buckets"][str(topic.id)]["doc_count"] > 0:
                            topic_matches.add(topic.id)
                    except (KeyError, IndexError, TypeError):
                        logger.warning(f"Failed to find aggregation result for topic {topic.id}")
            except Exception:
                logger.exception("Error in get_matching_topics", extra=dict(query=search_request, user=user.id))
        return topic_matches
