from newsroom.products.service import ProductsService
from newsroom.types import ProductResourceModel
from superdesk.core.resources import ResourceConfig, MongoResourceConfig, RestEndpointConfig
from content_api import MONGO_PREFIX
from superdesk.core.module import Module


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
