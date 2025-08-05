from quart_babel import lazy_gettext

from newsroom import MONGO_PREFIX
from newsroom.types import SectionFilterModel
from newsroom.web.factory import NewsroomWebApp
from superdesk.core.module import Module
from superdesk.core.resources import ResourceConfig, MongoIndexOptions, MongoResourceConfig

from .service import SectionFiltersService
from .views import get_settings_data, section_filters_endpoints

section_filters_config = ResourceConfig(
    name="section_filters",
    data_class=SectionFilterModel,
    service=SectionFiltersService,
    mongo=MongoResourceConfig(
        prefix=MONGO_PREFIX,
        indexes=[
            MongoIndexOptions(
                name="name",
                keys=[("name", 1), ("filter_type", 1)],
                unique=True,
                collation={"locale": "en", "strength": 2},
            )
        ],
    ),
    default_sort=[("name", 1)],
)


def init_module(app: NewsroomWebApp):
    app.wsgi.settings_app(
        "section-filters",
        lazy_gettext("Section Filters"),
        weight=450,
        data=get_settings_data,
    )


module = Module(
    name="newsroom.section_filters",
    resources=[section_filters_config],
    endpoints=[section_filters_endpoints],
    init=init_module,
)
