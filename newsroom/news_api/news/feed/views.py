from superdesk.core import get_current_async_app
from superdesk.core.types import SearchRequest
from superdesk.core.web import EndpointGroup, Request, Response, RestGetResponse


feed_endpoints = EndpointGroup("feed_endpoints", __name__)


@feed_endpoints.endpoint("news/feed-async", methods=["GET"])
async def news_feed(args, params: SearchRequest, request: Request):
    app = get_current_async_app()
    items_service = app.elastic.get_client_async("items")
    cursor, count = await items_service.find(params)

    response = RestGetResponse(
        _items=cursor.docs,
        _meta=dict(
            page=params.page,
            max_results=params.max_results,
            total=count,
        ),
    )

    return Response(response)
