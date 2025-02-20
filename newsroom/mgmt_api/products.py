from newsroom import MONGO_PREFIX
from newsroom.products.service import ProductsService
from newsroom.types import ProductResourceModel

from superdesk.core.module import Module
from superdesk.core.resources import MongoResourceConfig, ResourceConfig, RestEndpointConfig


products_resource_config = ResourceConfig(
    name="products",
    data_class=ProductResourceModel,
    service=ProductsService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    rest_endpoints=RestEndpointConfig(),
    uses_etag=False,
)

module = Module(
    name="newsroom.mgmt_api.products",
    resources=[products_resource_config],
)
