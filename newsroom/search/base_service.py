from typing import TypeVar, Generic, Any
from inspect import isawaitable


from superdesk.core.types import SortListParam, Request, Response, SearchRequest, RestGetResponse, ESQuery
from superdesk.core.resources import AsyncResourceService, ResourceModel
from superdesk.core.resources.cursor import ElasticsearchResourceCursorAsync

from newsroom.types import SectionEnum

from .types import NewshubSearchRequest, BaseSearchRequestArgs, SearchArgsType, SearchFilterFunction


SearchItemType = TypeVar("SearchItemType", bound=ResourceModel)


class BaseNewshubSearchService(Generic[SearchArgsType, SearchItemType]):
    """Base Newshub search service class to be used, mainly for Wire and Agenda resources"""

    #: The type for the search request args, mainly used for web requests
    search_args_class: type[SearchArgsType]

    #: The list of default filters for use when searching this resource
    filters: list[SearchFilterFunction]

    #: The name of the section for this resource
    section: SectionEnum

    #: The default sort to be applied, if one was not supplied by the request
    default_sort: SortListParam = [{"versioncreated", -1}]

    #: The default page size, if one was not supplied by the request
    default_page_size: int

    #: The underlying resource service used to run our elasticsearch queries
    service: AsyncResourceService[SearchItemType]

    async def process_web_request(self, request: Request) -> Response:
        """Process a request from the WebAPI

        :param request: The web request instance
        :returns: The search request response to be returned to the web client
        """

        search_request = self.get_search_request_instance(request)
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
        response, count = await self.get_search_response(internal_request, cursor)

        return Response(response, 200, [("X-Total-Count", count)])

    def get_search_request_instance(self, request: Request) -> NewshubSearchRequest[SearchArgsType]:
        """Constructs and returns an instance of NewshubSearchRequest based on the web request instance

        :param request: The web request instance
        :returns: The internal NewshubSearchRequest instance
        """

        return NewshubSearchRequest[SearchArgsType](
            section=self.section,
            web_request=request,
            args=self.search_args_class.from_url_args(request),
            search=ESQuery(),
        )

    async def run_filters_and_return_query(
        self, search_request: NewshubSearchRequest, filters: list[SearchFilterFunction] | None = None
    ) -> ESQuery:
        """Executes all the filters and returns the constructed elasticsearch query

        :param search_request: The internal NewshubSearchRequest instance to use
        :param filters: Optional list of filters to execute, defaults to filters defined on search service
        :returns: The elasticsearch query read
        """

        for search_filter in filters if filters is not None else self.filters:
            response = search_filter(search_request)
            if isawaitable(response):
                await response

        return search_request.search

    async def search(
        self, request: SearchArgsType | NewshubSearchRequest, filters: list[SearchFilterFunction] | None = None
    ) -> ElasticsearchResourceCursorAsync[SearchItemType]:
        """Runs a search against the resource service, based on supplied params

        :param request: Either the request args (SearchArgsType) or internal request (NewshubSearchRequest) instance
        :param filters: Optional list of filters to execute, defaults to filters defined on search service
        :returns: A cursor with the search results
        """

        if isinstance(request, NewshubSearchRequest):
            search_request = request
        else:
            search_request = NewshubSearchRequest(section=self.section, args=request)

        if search_request.section is None:
            search_request.section = self.section

        elastic_query = await self.run_filters_and_return_query(search_request, filters)
        internal_request = SearchRequest(
            sort=search_request.args.sort,
            max_results=search_request.args.page_size,
            page=search_request.args.page,
            aggregations=not search_request.args.page and search_request.args.aggs,
            projection=search_request.args.projection,
            elastic=elastic_query,
        )
        return await self.service.find(internal_request)

    async def get_search_response(
        self, internal_request: SearchRequest, cursor: ElasticsearchResourceCursorAsync[SearchItemType]
    ) -> tuple[dict[str, Any], int]:
        """Constructs a dictionary for use with REST response from a web request

        :param internal_request: The internal NewshubSearchRequest instance to use
        :param cursor: The cursor from the search request
        :returns: A tuple containing the dictionary to return to the client, and the count of documents from the search request
        """

        count = await cursor.count()
        response = RestGetResponse(
            _items=await cursor.to_list_raw(),
            _meta=dict(
                page=internal_request.page,
                max_results=internal_request.max_results
                if internal_request.max_results is not None
                else self.default_page_size,
                total=count,
            ),
        )
        cursor.extra(response)

        return response, count

    async def get_items_by_id(self, item_ids: list[str]) -> ElasticsearchResourceCursorAsync[SearchItemType]:
        """Helper function to search for items based on ID, applying filters for the current user

        :param item_ids: A list of IDs to search for
        :returns: A cursor with the search results
        """

        return await self.search(BaseSearchRequestArgs(ids=item_ids))
