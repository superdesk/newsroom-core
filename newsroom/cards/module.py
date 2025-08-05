from typing import cast
from asyncio import gather
from quart_babel import lazy_gettext

from superdesk.core.module import Module, SuperdeskAsyncApp
from superdesk.core.resources import ResourceConfig, MongoResourceConfig

from newsroom import MONGO_PREFIX
from newsroom.core import get_current_wsgi_app
from newsroom.utils import query_resource
from newsroom.navigations import NavigationsService

from newsroom.types import CardResourceModel
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

    cards_task = CardsResourceService().find({})
    navs_task = NavigationsService().search(lookup={"is_enabled": True})

    cards, navigations = await gather((await cards_task).to_list_raw(), (await navs_task).to_list_raw())

    return {
        "products": list(query_resource("products", lookup={"is_enabled": True})),
        "cards": cards,
        "dashboards": app.dashboards,
        "navigations": navigations,
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
