from newsroom.wire.search import WireSearchResource, WireSearchService
from newsroom.wire import WireSearchServiceAsync
from newsroom.types import SectionEnum


class FactCheckSearchResource(WireSearchResource):
    pass


class FactCheckSearchService(WireSearchService):
    section = "factcheck"


class FactCheckSearchServiceAsync(WireSearchServiceAsync):
    section = SectionEnum.FACTCHECK
