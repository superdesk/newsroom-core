from typing import cast

from quart_babel import lazy_gettext

from superdesk.core.module import Module, SuperdeskAsyncApp
from superdesk.core.resources import ResourceConfig, MongoResourceConfig

from newsroom import MONGO_PREFIX
from newsroom.core import get_current_wsgi_app
from newsroom.utils import query_resource

from .model import CardResourceModel
from .service import CardsResourceService
from .views import cards_endpoints


cards_resource_config = ResourceConfig(
    name="cards",
    data_class=CardResourceModel,
    service=CardsResourceService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    default_sort=[("order", 1), ("label", 1)],
)


async def get_settings_data():
    app = get_current_wsgi_app()

    return {
        "products": list(query_resource("products", lookup={"is_enabled": True})),
        "cards": await (await CardsResourceService().find({})).to_list_raw(),
        "dashboards": app.dashboards,
        "navigations": list(query_resource("navigations", lookup={"is_enabled": True})),
    }


def init_app(app: SuperdeskAsyncApp):
    from newsroom.web.factory import NewsroomWebApp

    wsgi = cast(NewsroomWebApp, app.wsgi)
    wsgi.settings_app(
        "cards",
        lazy_gettext("Dashboards"),
        weight=500,
        data=get_settings_data,
    )


module = Module(
    name="newsroom.cards",
    resources=[cards_resource_config],
    endpoints=[cards_endpoints],
    init=init_app,
)
