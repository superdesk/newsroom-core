from superdesk.core.module import Module, SuperdeskAsyncApp
from superdesk.core.resources import ResourceConfig, MongoResourceConfig
from superdesk.core.web import EndpointGroup

from newsroom import MONGO_PREFIX
from newsroom.types import MonitoringProfileResourceModel
from newsroom.formatters import register_formatter

from .service import MonitoringProfileService
from .formatters.pdf_formatter import MonitoringPDFFormatter
from .formatters.rtf_formatter import MonitoringRTFFormatter


monitoring_endpoints = EndpointGroup("monitoring", __name__)

monitoring_resource_config = ResourceConfig(
    name="monitoring",
    data_class=MonitoringProfileResourceModel,
    service=MonitoringProfileService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    default_sort=[("name", 1)],
)


def init_module(app: SuperdeskAsyncApp) -> None:
    register_formatter(MonitoringPDFFormatter)
    register_formatter(MonitoringRTFFormatter)


module = Module(
    "newsroom.monitoring",
    endpoints=[monitoring_endpoints],
    resources=[monitoring_resource_config],
    init=init_module,
)

from . import views  # noqa
