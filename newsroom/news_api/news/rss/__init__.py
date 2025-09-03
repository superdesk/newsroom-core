from superdesk.core.module import Module
from .views import rss_endpoints

module = Module(name="newsroom.news_api.rss", endpoints=[rss_endpoints])
