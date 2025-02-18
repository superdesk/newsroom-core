from newsroom import MONGO_PREFIX
from newsroom.products.service import ProductsService
from newsroom.types import ProductResourceModel

from superdesk.core.module import Module
from superdesk.core.resources import MongoResourceConfig, ResourceConfig, RestEndpointConfig


class CPProductResourceModel(ProductResourceModel):
    pass


class CPProductsService(ProductsService):
    resource_name = "products"


products_resource_config = ResourceConfig(
    name="products",
    data_class=CPProductResourceModel,
    service=CPProductsService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    rest_endpoints=RestEndpointConfig(auth=False),
    uses_etag=False,
)

module = Module(
    name="newsroom.mgmt_api.products",
    resources=[products_resource_config],
)
