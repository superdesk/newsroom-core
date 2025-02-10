from newsroom.navigations import NavigationsService
from superdesk.core.resources import ResourceConfig, MongoResourceConfig
from content_api import MONGO_PREFIX
from newsroom.types import NavigationModel
from superdesk.core.web import EndpointGroup
from superdesk.core.module import Module

navigation_resource_config = ResourceConfig(
    name="navigations",
    data_class=NavigationModel,
    service=NavigationsService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
)

navigations_endpoints = EndpointGroup("navigations", __name__)

module = Module(
    name="newsroom.mgmt_api.navigations",
    resources=[navigation_resource_config],
    endpoints=[navigations_endpoints],
)
