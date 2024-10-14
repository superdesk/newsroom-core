from superdesk.core.module import SuperdeskAsyncApp, Module
from .views import atom_endpoints


def init_module(app: SuperdeskAsyncApp):
    app.wsgi.register_endpoint(atom_endpoints)


module = Module(
    name="newsroom.news_api.atom",
    init=init_module,
)
