from superdesk.core.module import SuperdeskAsyncApp, Module
from .views import assets_endpoints


def init_module(app: SuperdeskAsyncApp):
    app.wsgi.register_endpoint(assets_endpoints)


module = Module(
    name="newsroom.news_api.assets",
    init=init_module,
)
