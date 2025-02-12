from newsroom.navigations import NavigationsService
from newsroom.navigations.module import navigations_resource_config
from superdesk.core.resources import ResourceConfig, MongoResourceConfig, RestEndpointConfig, RestParentLink
from content_api import MONGO_PREFIX
from newsroom.types import NavigationModel
from superdesk.core.module import Module
from newsroom.mgmt_api.auth import JWTTokenAuth


class CPNavigationModel(NavigationModel):
    pass


class CPNavigationsService(NavigationsService):
    pass


navigation_resource_config = ResourceConfig(
    name="navigations",
    data_class=CPNavigationModel,
    service=CPNavigationsService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    rest_endpoints=RestEndpointConfig(
        resource_methods=["GET", "POST"], item_methods=["GET", "PATCH", "DELETE"], auth=JWTTokenAuth, url="navigations"
    ),
)

module = Module(
    name="newsroom.mgmt_api.navigations",
    resources=[navigation_resource_config],
)
