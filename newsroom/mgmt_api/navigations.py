from newsroom import MONGO_PREFIX
from newsroom.navigations import NavigationsService
from newsroom.types import NavigationModel

from superdesk.core.module import Module
from superdesk.core.resources import MongoResourceConfig, ResourceConfig, RestEndpointConfig


class CPNavigationModel(NavigationModel):
    pass


class CPNavigationsService(NavigationsService):
    pass


navigation_resource_config = ResourceConfig(
    name="navigations",
    data_class=CPNavigationModel,
    service=CPNavigationsService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    rest_endpoints=RestEndpointConfig(auth=False),
)

module = Module(
    name="newsroom.mgmt_api.navigations",
    resources=[navigation_resource_config],
)
