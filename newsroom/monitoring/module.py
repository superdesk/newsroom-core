from superdesk.core.module import Module
from superdesk.core.resources import ResourceConfig, MongoResourceConfig
from superdesk.core.web import EndpointGroup

from newsroom import MONGO_PREFIX
from newsroom.types import MonitoringProfileResourceModel
from .service import MonitoringProfileService


monitoring_endpoints = EndpointGroup("monitoring", __name__)

monitoring_resource_config = ResourceConfig(
    name="monitoring",
    data_class=MonitoringProfileResourceModel,
    service=MonitoringProfileService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    default_sort=[("name", 1)],
)

module = Module(
    "newsroom.monitoring",
    endpoints=[monitoring_endpoints],
    resources=[monitoring_resource_config],
)

from . import views  # noqa
