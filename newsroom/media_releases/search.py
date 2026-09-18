from newsroom.wire.search import WireSearchResource, WireSearchService
from newsroom.wire import WireSearchServiceAsync
from newsroom.types import SectionEnum


class MediaReleasesSearchResource(WireSearchResource):
    pass


class MediaReleasesSearchService(WireSearchService):
    section = "media_releases"
    limit_days_setting = "media_releases_time_limit_days"


class MediaReleasesSearchServiceAsync(WireSearchServiceAsync):
    section = SectionEnum.MEDIA_RELEASES
    limit_days_setting = "media_releases_time_limit_days"
