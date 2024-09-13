from .model import SectionFilter
from .service import SectionFiltersService

from .module import module  # noqa

__all__ = ["SectionFilter", "SectionFiltersService"]


def init_app(app):
    # TODO-Async: Remove this once agenda, news_api.news, search and wire are migrated to async
    import superdesk
    from .section_filters import SectionFiltersResource, SectionFiltersService

    superdesk.register_resource("section_filters", SectionFiltersResource, SectionFiltersService, _app=app)
