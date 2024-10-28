from newsroom import MONGO_PREFIX
from newsroom.agenda.service import FeaturedService

from newsroom.types import FeaturedResourceModel
from superdesk.core.module import Module
from superdesk.core.resources import ResourceConfig, MongoResourceConfig


featured_resource_config = ResourceConfig(
    name="agenda_featured",
    data_class=FeaturedResourceModel,
    service=FeaturedService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
)

module = Module(name="newsroom.agenda", resources=[featured_resource_config])
