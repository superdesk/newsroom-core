from newsroom.core.resources.service import NewshubAsyncResourceService
from .model import SectionFilter


class SectionFiltersService(NewshubAsyncResourceService[SectionFilter]):
    resource_name = "section_filters"
