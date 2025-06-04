import logging

from newsroom.wire.search import WireSearchResource, WireSearchService
from newsroom.wire import WireSearchServiceAsync
from newsroom.types import SectionEnum

logger = logging.getLogger(__name__)


class MarketPlaceSearchResource(WireSearchResource):
    pass


class MarketPlaceSearchService(WireSearchService):
    section = "aapX"
    limit_days_setting = "aapx_time_limit_days"


class MarketPlaceSearchServiceAsync(WireSearchServiceAsync):
    section = SectionEnum.MARKET_PLACE
    limit_days_setting = "aapx_time_limit_days"
