from superdesk.core.module import Module
from superdesk.core.resources import ResourceConfig, MongoResourceConfig, MongoIndexOptions, ElasticResourceConfig
from superdesk.core.web import EndpointGroup

from newsroom import MONGO_PREFIX, ELASTIC_PREFIX
from newsroom.types import WireItem

from .service import WireItemService

wire_endpoints = EndpointGroup("wire", __name__)

wire_items_resource_config = ResourceConfig(
    name="items",
    data_class=WireItem,
    service=WireItemService,
    default_sort=[("versioncreated", -1)],
    versioning=True,
    mongo=MongoResourceConfig(
        prefix=MONGO_PREFIX,
        indexes=[
            MongoIndexOptions(
                name="_ancestors_",
                keys=[("ancestors", 1)],
                unique=False,
            ),
            MongoIndexOptions(
                name="expiry_1",
                keys=[("expiry", 1)],
                unique=False,
            ),
            MongoIndexOptions(
                name="evolvedfrom_1",
                keys=[("evolvedfrom", 1)],
                unique=False,
            ),
        ],
    ),
    elastic=ElasticResourceConfig(
        prefix=ELASTIC_PREFIX,
        filter={"bool": {"must_not": {"term": {"type": "composite"}}}},
    ),
)

module = Module("newsroom.wire", endpoints=[wire_endpoints], resources=[wire_items_resource_config])

from . import views  # noqa
