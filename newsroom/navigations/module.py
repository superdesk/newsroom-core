from typing import TYPE_CHECKING
from quart_babel import lazy_gettext
from superdesk.core.module import Module
from superdesk.core.resources import ResourceConfig, MongoResourceConfig

from newsroom import MONGO_PREFIX

from .model import Navigation
from .views import get_settings_data, navigations_endpoints
from .service import NavigationsService

if TYPE_CHECKING:
    from newsroom.web.factory import NewsroomWebApp

navigations_resource_config = ResourceConfig(
    name="navigations",
    data_class=Navigation,
    service=NavigationsService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    default_sort=[("order", 1), ("name", 1)],
)


def init_module(app: "NewsroomWebApp"):
    app.wsgi.settings_app(
        "navigations",
        lazy_gettext("Global Topics"),
        weight=300,
        data=get_settings_data,
    )


module = Module(
    name="newsroom.navigations",
    resources=[navigations_resource_config],
    endpoints=[navigations_endpoints],
    init=init_module,
)
