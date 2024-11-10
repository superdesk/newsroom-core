from superdesk.core.module import Module, SuperdeskAsyncApp
from superdesk.core.resources import ResourceConfig, MongoResourceConfig, ElasticResourceConfig
from superdesk.core.web import EndpointGroup

from newsroom.types import FeaturedResourceModel, AgendaItem
from newsroom import MONGO_PREFIX, ELASTIC_PREFIX
from newsroom.search.config import init_nested_aggregation

from .agenda_search import AgendaItemService, AgendaSearchServiceAsync
from .filters import PRIVATE_FIELDS, aggregations
from .featured_service import FeaturedService


agenda_endpoints = EndpointGroup("agenda", __name__)


agenda_items_resource_config = ResourceConfig(
    name="agenda",
    data_class=AgendaItem,
    service=AgendaItemService,
    default_sort=[("dates.start", 1)],
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    elastic=ElasticResourceConfig(prefix=ELASTIC_PREFIX),
)

featured_resource_config = ResourceConfig(
    name="agenda_featured",
    data_class=FeaturedResourceModel,
    service=FeaturedService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
)


def init_module(app: SuperdeskAsyncApp):
    configured_page_size = app.wsgi.config.get("AGENDA_PAGE_SIZE")
    if configured_page_size is not None:
        AgendaSearchServiceAsync.default_page_size = configured_page_size

    if app.wsgi.config.get("AGENDA_HIDE_COVERAGE_ASSIGNEES"):
        PRIVATE_FIELDS.extend(["*.assigned_desk_*", "*.assigned_user_*"])

    init_nested_aggregation("agenda", ["subject"], app.wsgi.config.get("AGENDA_GROUPS", []), aggregations)


module = Module(
    name="newsroom.agenda",
    init=init_module,
    endpoints=[agenda_endpoints],
    resources=[
        featured_resource_config,
        agenda_items_resource_config,
    ],
)
