import superdesk

from .resource import NewsAPISearchResource
from .service import NewsAPISearchService

from superdesk.core.module import Module
from .views import news_api_search_endpoints

module = Module(name="newsroom.news_api.search", endpoints=[news_api_search_endpoints])


def init_app(app):
    superdesk.register_resource("news/search1", NewsAPISearchResource, NewsAPISearchService, _app=app)
