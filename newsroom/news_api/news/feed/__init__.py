from superdesk.core.module import Module
from .views import news_api_feed_endpoints

module = Module(name="newsroom.news_api.feed", endpoints=[news_api_feed_endpoints])
