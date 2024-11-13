from superdesk.core.web import EndpointGroup
from superdesk.core.types import Request

from ..search_service_async import NewsApiSearchServiceAsync

news_api_search_endpoints = EndpointGroup("news_api_search", __name__)


@news_api_search_endpoints.endpoint("news/search", methods=["GET"])
async def news_api_search(request: Request):
    return await NewsApiSearchServiceAsync().process_web_request(request)
