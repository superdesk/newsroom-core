from superdesk.core.module import Module
from .views import news_api_search_endpoints

module = Module(name="newsroom.news_api.search", endpoints=[news_api_search_endpoints])
