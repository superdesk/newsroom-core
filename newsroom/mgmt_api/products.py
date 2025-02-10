from newsroom.products.products import ProductsService
from newsroom.types import ProductResourceModel
from superdesk.core.resources import ResourceConfig, MongoResourceConfig
from content_api import MONGO_PREFIX
from superdesk.core.web import EndpointGroup
from superdesk.core.module import Module

products_resource_config = ResourceConfig(
    name="products",
    data_class=ProductResourceModel,
    service=ProductsService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
)

products_endpoints = EndpointGroup("products", __name__)

module = Module(
    name="newsroom.mgmt_api.products",
    resources=[products_resource_config],
    endpoints=[products_endpoints],
)
