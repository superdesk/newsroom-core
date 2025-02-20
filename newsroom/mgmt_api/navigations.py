from newsroom import MONGO_PREFIX
from newsroom.navigations import NavigationsService
from newsroom.types import NavigationModel

from superdesk.core.module import Module
from superdesk.core.resources import MongoResourceConfig, ResourceConfig, RestEndpointConfig


navigation_resource_config = ResourceConfig(
    name="navigations",
    data_class=NavigationModel,
    service=NavigationsService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    rest_endpoints=RestEndpointConfig(),
)

module = Module(
    name="newsroom.mgmt_api.navigations",
    resources=[navigation_resource_config],
)
