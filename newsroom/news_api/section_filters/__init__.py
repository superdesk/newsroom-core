import superdesk

from newsroom.section_filters.section_filters import SectionFiltersService, SectionFiltersResource


# TODO-ASYNC: remove this once news_api modules are migrate to async
def init_app(app):
    superdesk.register_resource("section_filters", NewsAPISectionFilterResource, SectionFiltersService, _app=app)


class NewsAPISectionFilterResource(SectionFiltersResource):
    """
    Overload the newsroom section filter resource so we can set it to be an internal resource
    """

    internal_resource = True
