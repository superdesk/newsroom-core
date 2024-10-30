from typing import Any, cast
from datetime import datetime, timedelta
import logging

from bson import ObjectId

from content_api.items.model import PubStatusType
from superdesk.core.types import Request, Response, SearchRequest, ESQuery, ESBoolQuery
from superdesk.core import get_app_config
from superdesk.core.resources import AsyncResourceService
from superdesk.core.resources.cursor import ElasticsearchResourceCursorAsync

from newsroom.exceptions import AuthorizationError
from newsroom.types import SectionEnum, Product, TopicResourceModel, UserResourceModel, CompanyResource, WireItem
from newsroom.auth.utils import get_user_or_none_from_request, get_user_sections
from newsroom.search.types import NewshubSearchRequest, SearchFilterFunction
from newsroom.search.base_service import BaseNewshubSearchService
from newsroom.search.filters import (
    apply_query_string,
    apply_date_range,
    apply_advanced_search,
    prefill_user,
    prefill_company,
    prefill_products,
    prefill_args_from_topic,
    apply_section_filter,
    apply_company_filter,
    apply_products_filter,
    validate_request,
    apply_ids_filter,
)
from newsroom.products.products import get_products_by_navigation

from .filters import (
    WireSearchRequestArgs,
    default_wire_filters,
    apply_item_type_filter,
    apply_filters,
    apply_embargoed_filters,
    apply_not_canceled_filter,
    apply_time_limit_filter,
)


logger = logging.getLogger(__name__)


class WireItemService(AsyncResourceService[WireItem]):
    async def insert_versioned_document(self, doc_dict: dict[str, Any]):
        await super().insert_versioned_document(doc_dict)

        if doc_dict.get("pubstatus") == PubStatusType.CANCELLED.value:
            # If the update is a cancel, we need to cancel all versions
            await self.mongo_versioned_async.update_many(
                {
                    "_id_document": doc_dict["_id_document"],
                    "pubstatus": {"$ne": PubStatusType.CANCELLED.value},
                },
                {"$set": {"pubstatus": PubStatusType.CANCELLED.value}},
            )


class WireSearchServiceAsync(BaseNewshubSearchService[WireSearchRequestArgs, WireItem]):
    search_args_class = WireSearchRequestArgs
    filters = default_wire_filters
    section = SectionEnum.WIRE
    default_sort = [{"versioncreated", -1}]
    default_page_size = 25

    def __init__(self):
        self.service = WireItemService()

    async def get_current_user_bookmarks_count(self, section: SectionEnum | None = None) -> int:
        user = get_user_or_none_from_request(None)
        if not user:
            return 0

        cursor = await self.search(
            NewshubSearchRequest(
                section=section or self.section,
                args=WireSearchRequestArgs(bookmarks=[user.id], page_size=0),
            )
        )
        return await cursor.count()

    async def get_items_by_id(
        self, item_ids: list[str], args: WireSearchRequestArgs | None = None, apply_permissions: bool = False
    ) -> ElasticsearchResourceCursorAsync[WireItem]:
        if args is None:
            args = WireSearchRequestArgs()

        args.ids = item_ids
        return await self.search(
            args,
            filters=None
            if apply_permissions
            else [
                apply_item_type_filter,
                apply_ids_filter,
            ],
        )

    async def get_items_for_action(self, item_ids: list[str]):
        cursor = await self.get_items_by_id(item_ids, args=WireSearchRequestArgs(ignore_latest=True))
        async for item in cursor:
            if item.slugline and item.anpa_take_key:
                item.slugline = f"{item.slugline} | {item.anpa_take_key}"

        return cursor

    async def process_web_request(self, request: Request) -> Response:
        search_request = self.get_search_request_instance(request)

        # If ``prepend_embargoed`` is not in url args and PREPEND_EMBARGOED_TO_WIRE_SEARCH is True
        # then enable it, and disable the other params
        if request.get_url_arg("prepend_embargoed") is None and get_app_config("PREPEND_EMBARGOED_TO_WIRE_SEARCH"):
            search_request.args.prepend_embargoed = True
            search_request.args.exclude_embargoed = True
            search_request.args.embargoed_only = False

        if search_request.args.all_versions:
            internal_request, cursor = await self._search_all_versions(search_request)
        else:
            elastic_query = await self.run_filters_and_return_query(search_request)
            internal_request = SearchRequest(
                sort=search_request.args.sort,
                max_results=search_request.args.page_size,
                page=search_request.args.page,
                aggregations=not search_request.args.page and search_request.args.aggs,
                projection=search_request.args.projection,
                elastic=elastic_query,
            )
            cursor = await self.service.find(internal_request)

        if search_request.args.prepend_embargoed:
            await self.prepend_embargoed_items_to_response(search_request, cursor)

        response, count = await self.get_search_response(internal_request, cursor)

        matched_ids: list[str] = request.storage.request.get("matched_ids", [])
        if matched_ids:
            response.setdefault("_links", {})["matched_ids"] = matched_ids

        return Response(response, 200, [("X-Total-Count", count)])

    async def _search_all_versions(
        self, search_request: NewshubSearchRequest[WireSearchRequestArgs]
    ) -> tuple[SearchRequest, ElasticsearchResourceCursorAsync[WireItem]]:
        search_request.args.ignore_latest = True
        elastic_query = await self.run_filters_and_return_query(search_request)
        # await self.validate_request(search_request)

        # Search up to 1,000 items to make sure pagination works
        # as we're getting all versions here
        # where as the final response will only include the last version
        # of each content chain
        original_size = search_request.args.page_size
        original_page = search_request.args.page
        search_request.args.page_size = 1000
        search_request.args.page = 0

        internal_request = SearchRequest(
            sort=search_request.args.sort,
            max_results=search_request.args.page_size,
            page=search_request.args.page,
            aggregations=not search_request.args.page and search_request.args.aggs,
            projection=search_request.args.projection,
            elastic=elastic_query,
        )

        cursor = await self.service.find(internal_request)
        next_item_ids: list[str] = []
        matched_ids: list[str] = []
        async for doc in cursor:
            matched_ids.append(doc.id)
            next_item_ids.append(await self.get_last_version_ids(doc))

        if search_request.web_request is not None:
            # Store the matched_ids so we can append to the response metadata
            search_request.web_request.storage.request.set("matched_ids", matched_ids)

        # Now run a query only using the IDs from the above search
        # This final search makes sure pagination still works
        search_request.args.page_size = original_size
        search_request.args.page = original_page
        internal_request.elastic.query.must = []
        internal_request.elastic.query.must_not = []
        internal_request.elastic.query.should = []
        internal_request.elastic.query.filter = [{"ids": {"values": next_item_ids}}]
        internal_request = SearchRequest(
            sort=search_request.args.sort,
            max_results=search_request.args.page_size,
            page=search_request.args.page,
            aggregations=not search_request.args.page and search_request.args.aggs,
            projection=search_request.args.projection,
            elastic=elastic_query,
        )
        result_cursor = await self.service.find(internal_request)
        # Use count from original requiest
        result_cursor.hits["hits"]["total"] = await cursor.count()
        return internal_request, result_cursor

    async def get_last_version_ids(self, doc: WireItem) -> str:
        if not doc.nextversion:
            # This is already the latest version
            return str(doc.id)
        elif doc.original_id:
            # Attempt to get the last version in the series using Elastic
            original_id = doc.original_id
            cursor = await self.service.search(
                {
                    "query": {
                        "bool": {
                            "filter": [
                                {"term": {"original_id": original_id}},
                            ],
                            "must_not": [{"exists": {"field": "nextversion"}}],
                        }
                    },
                    "size": 1,
                }
            )
            if await cursor.count():
                return str((await cursor.next_raw())["_id"])
            else:
                logger.warning(f'Failed to find the latest version using `original_id="{original_id}"`')

        # Either the item doesn't have ``original_id`` set, or the elastic query didn't find a match
        # So we resort to a slower method
        # This can happen for item's that were published prior to this new feature
        nextversion_id = doc.nextversion
        next_doc = await self.service.find_by_id(nextversion_id)
        if next_doc:
            return await self.get_last_version_ids(next_doc)
        else:
            # If, for whatever reason, we can't get the next version return the current one.
            # That way the request will still be fulfilled,
            # albeit with this content group cut short in versions
            item_id = doc.id
            logger.warning(f'Failed to find the next doc "{nextversion_id}" for "{item_id}"')
            return str(doc.id)

    async def prepend_embargoed_items_to_response(
        self,
        search_request: NewshubSearchRequest[WireSearchRequestArgs],
        cursor: ElasticsearchResourceCursorAsync[WireItem],
    ):
        search_request.args.exclude_embargoed = False
        search_request.args.prepend_embargoed = False
        search_request.args.embargoed_only = True
        search_request.search = ESQuery()
        elastic_query = await self.run_filters_and_return_query(search_request)
        internal_request = SearchRequest(
            sort=search_request.args.sort,
            max_results=search_request.args.page_size,
            page=search_request.args.page,
            aggregations=not search_request.args.page and search_request.args.aggs,
            projection=search_request.args.projection,
            elastic=elastic_query,
        )
        embargoed_cursor = await self.service.find(internal_request)

        if (await embargoed_cursor.count()) > 0:
            cursor.hits["hits"]["hits"] = embargoed_cursor.hits["hits"]["hits"] + cursor.hits["hits"]["hits"]
            cursor.hits["hits"]["total"] = await embargoed_cursor.count() + await cursor.count()

    # TODO-ASYNC: Convert to async Product model when available
    async def get_product_items_for_dashboard(
        self, product: Product, size: int, exclude_embargoed: bool = False
    ) -> list[WireItem]:
        def prefill_requested_product(request: NewshubSearchRequest):
            request.products = [product]

        cursor = await self.search(
            WireSearchRequestArgs(
                product_ids=[product["_id"]],
                page_size=size,
                exclude_embargoed=not get_app_config("DASHBOARD_EMBARGOED") or exclude_embargoed,
            ),
            # Provide custom filters so we can get items for the supplied product
            # even if the current user/company doesn't have permission for them
            # as the Dashboard allows this access
            filters=[
                prefill_user,
                prefill_company,
                prefill_requested_product,
                # Filters applied for section, item type, company type and the supplied product only
                apply_section_filter,
                apply_item_type_filter,
                apply_company_filter,
                apply_products_filter,
                # Make sure the request has been validated
                validate_request,
            ],
        )
        return await cursor.to_list()

    async def get_topic_items_query(
        self,
        topic: TopicResourceModel | None,
        user: UserResourceModel | None,
        company: CompanyResource | None,
        query: ESQuery | None = None,
        args: WireSearchRequestArgs | None = None,
    ) -> ESQuery | None:
        def prefill_request(request: NewshubSearchRequest):
            if topic:
                request.topic = topic
            if user:
                request.user = request.current_user = user
                request.is_admin = request.user.is_admin()
            else:
                request.is_admin = False

            if company:
                request.company = company
            if query:
                request.search = query

            if user is None and topic is not None and topic.navigation is not None:
                # TODO-ASYNC: Convert to Async service when it's available
                request.products = get_products_by_navigation(topic.navigation)

        search_request = NewshubSearchRequest(
            section=self.section,
            web_request=None,
            args=args or WireSearchRequestArgs(),
            search=query or ESQuery(),
        )

        filters: list[SearchFilterFunction] = [
            # Pre-fill the request arguments
            prefill_request,
            prefill_args_from_topic,
            # Apply standard filters used to match a topic
            apply_products_filter,
            apply_embargoed_filters,
            apply_query_string,
            apply_ids_filter,
            apply_filters,
            apply_advanced_search,
            apply_date_range,
        ]

        if user is not None:
            # If this query is from a User's perspective, then add
            # validation and section/company filters
            filters.extend(
                [
                    prefill_products,
                    # Make sure the request has been validated
                    validate_request,
                    # Base topics:
                    apply_section_filter,
                    apply_item_type_filter,
                    apply_company_filter,
                    apply_time_limit_filter,
                ]
            )

        try:
            return await self.run_filters_and_return_query(search_request, filters)
        except AuthorizationError:
            if user and topic:
                logger.info(f"Notification for user:{user.id} and topic:{topic.id} is skipped")
            pass

        return None

    async def get_mathing_topics_for_item(
        self,
        item_id: str,
        topics: list[TopicResourceModel],
        users: list[UserResourceModel],
        companies: dict[ObjectId, CompanyResource],
    ) -> set[ObjectId]:
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
                search_results: ElasticsearchResourceCursorAsync[WireItem] = await self.service.find(search_request)
                for topic in queried_topics:
                    try:
                        if search_results.hits["aggregations"]["topics"]["buckets"][str(topic.id)]["doc_count"] > 0:
                            topic_matches.add(topic.id)
                    except (KeyError, IndexError, TypeError):
                        logger.warning(f"Failed to find aggregation result for topic {topic.id}")
            except Exception:
                logger.exception("Error in get_matching_topics", extra=dict(query=search_request, user=user.id))

        return topic_matches

    async def get_matching_item_bookmarks(
        self, item_ids: list[str], users: dict[ObjectId, UserResourceModel], companies: dict[ObjectId, CompanyResource]
    ) -> set[ObjectId]:
        bookmark_users: set[ObjectId] = set()

        search_request = NewshubSearchRequest(
            section=self.section,
            web_request=None,
            args=WireSearchRequestArgs(ids=item_ids, ignore_latest=True),
            search=ESQuery(),
        )
        filters: list[SearchFilterFunction] = [
            apply_item_type_filter,
            apply_ids_filter,
            apply_section_filter,
        ]

        query = await self.run_filters_and_return_query(search_request, filters)
        cursor = await self.service.find(SearchRequest(elastic=query))

        if not await cursor.count():
            return bookmark_users

        async for item in cursor:
            for bookmark in item.bookmarks or []:
                user = users.get(bookmark)
                if user and (user.is_admin() or (user.company and companies.get(user.company))):
                    bookmark_users.add(user.id)

        return bookmark_users

    async def get_product_item_report(self, product: Product) -> ElasticsearchResourceCursorAsync[WireItem]:
        now = datetime.utcnow()
        aggs = {
            "today": {
                "date_range": {
                    "field": "versioncreated",
                    "ranges": [{"from": now.strftime("%Y-%m-%d")}],
                }
            },
            "last_24_hours": {
                "date_range": {
                    "field": "versioncreated",
                    "ranges": [{"from": "now-1d/d"}],
                }
            },
            "this_week": {
                "date_range": {
                    "field": "versioncreated",
                    "ranges": [{"from": (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")}],
                }
            },
            "last_7_days": {
                "date_range": {
                    "field": "versioncreated",
                    "ranges": [{"from": (now - timedelta(days=7)).strftime("%Y-%m-%d")}],
                }
            },
            "this_month": {
                "date_range": {
                    "field": "versioncreated",
                    "ranges": [{"from": (now.replace(day=1)).strftime("%Y-%m-%d")}],
                }
            },
            "previous_month": {
                "date_range": {
                    "field": "versioncreated",
                    "ranges": [
                        {
                            "from": (((now.replace(day=1)) - timedelta(days=1)).replace(day=1)).strftime("%Y-%m-%d"),
                            "to": (now.replace(day=1)).strftime("%Y-%m-%d"),
                        }
                    ],
                }
            },
            "last_6_months": {
                "date_range": {
                    "field": "versioncreated",
                    "ranges": [{"from": (now - timedelta(days=180)).strftime("%Y-%m-%d")}],
                }
            },
        }

        return await self.search(
            NewshubSearchRequest(
                section=cast(SectionEnum | None, product.get("product_type")) or self.section or SectionEnum.WIRE,
                products=[product],
                args=WireSearchRequestArgs(page_size=0),
                search=ESQuery(aggs=aggs),
            ),
            filters=[
                apply_section_filter,
                apply_item_type_filter,
                apply_not_canceled_filter,
            ],
        )
