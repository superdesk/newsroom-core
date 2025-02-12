from newsroom.navigations import NavigationsService
from superdesk.core.resources import ResourceConfig, MongoResourceConfig, RestEndpointConfig
from content_api import MONGO_PREFIX
from newsroom.types import NavigationModel
from superdesk.core.module import Module


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
