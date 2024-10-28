from superdesk.core.module import Module
from .views import assets_endpoints

module = Module(name="newsroom.news_api.assets", endpoints=[assets_endpoints])
