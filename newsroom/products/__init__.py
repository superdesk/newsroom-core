from quart_babel import lazy_gettext

import superdesk
from superdesk.core.types import MongoResourceConfig
from superdesk.core.module import Module
from superdesk.core.app import SuperdeskAsyncApp
from superdesk.core.resources import ResourceConfig

from newsroom import MONGO_PREFIX
from newsroom.types import ProductResourceModel
from newsroom.core import NewshubModuleConfig

from . import products
from .service import ProductsService
from .views import get_settings_data, products_endpoints
from .utils import (
    get_products_by_company,
    get_products_by_company_async,
    get_products_by_user_async,
    get_products_by_navigation_async,
    get_products_for_request_user_and_company,
)

__all__ = [
    "get_products_by_company",
    "get_products_by_company_async",
    "get_products_by_user_async",
    "get_products_by_navigation_async",
    "get_products_for_request_user_and_company",
    "ProductsService",
]


def init_module(app: SuperdeskAsyncApp):
    if products_config.register_settings:
        app.wsgi.settings_app("products", lazy_gettext("Products"), weight=400, data=get_settings_data)

    # TODO-ASYNC: Remove when products is fully async
    products.products_service = products.ProductsService("products", superdesk.get_backend())
    products.ProductsResource("products", app.wsgi, products.products_service)

    if products_config.register_endpoints:
        app.wsgi.register_endpoint(products_endpoints)


products_resource_config = ResourceConfig(
    name="products",
    data_class=ProductResourceModel,
    service=ProductsService,
    default_sort=[("name", 1)],
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
)

products_config = NewshubModuleConfig()
module = Module(
    name="newsroom.products",
    resources=[products_resource_config],
    config=products_config,
    init=init_module,
    endpoints=[],
)
