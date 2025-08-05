from superdesk.core.web import EndpointGroup
from superdesk.core.types import Request

from .service import NewsAPIFeedSearchService

news_api_feed_endpoints = EndpointGroup("news_api_feed", __name__)


@news_api_feed_endpoints.endpoint("news/feed", methods=["GET"])
async def news_api_search(request: Request):
    return await NewsAPIFeedSearchService().process_web_request(request)
