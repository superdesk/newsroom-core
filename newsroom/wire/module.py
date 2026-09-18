from superdesk.core.module import Module, SuperdeskAsyncApp
from superdesk.core.resources import ResourceConfig, MongoResourceConfig, MongoIndexOptions, ElasticResourceConfig
from superdesk.core.web import EndpointGroup

from newsroom import MONGO_PREFIX, ELASTIC_PREFIX
from newsroom.types import WireItem
from newsroom.core import NewshubModuleConfig
from newsroom.formatters import register_formatter

from .service import WireItemService
from .formatters import (
    TextFormatter,
    NITFFormatter,
    NewsMLG2Formatter,
    JsonFormatter,
    PictureFormatter,
    NINJSFormatter,
    NINJSFormatter2,
    HTMLFormatter,
    HTMLMediaFormatter,
    HTMLPackageFormatter,
    NINJSWithoutEmbedsFormatter,
    NINJSPackageFormatter,
)

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


def init_module(app: SuperdeskAsyncApp) -> None:
    register_formatter(TextFormatter)
    register_formatter(NITFFormatter)
    register_formatter(NewsMLG2Formatter)
    register_formatter(JsonFormatter)
    register_formatter(NINJSFormatter)
    register_formatter(NINJSFormatter2)
    register_formatter(HTMLFormatter)
    register_formatter(HTMLMediaFormatter)
    register_formatter(HTMLPackageFormatter)
    register_formatter(NINJSWithoutEmbedsFormatter)
    register_formatter(NINJSPackageFormatter)

    if app.wsgi.config.get("ALLOW_PICTURE_DOWNLOAD", True):
        register_formatter(PictureFormatter)

    if wire_module_config.register_endpoints:
        app.wsgi.register_endpoint(wire_endpoints)


wire_module_config = NewshubModuleConfig()
module = Module(
    "newsroom.wire",
    endpoints=[],
    resources=[wire_items_resource_config],
    init=init_module,
    config=wire_module_config,
)

from . import views  # noqa
