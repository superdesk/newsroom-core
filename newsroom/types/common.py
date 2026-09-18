from enum import Enum, unique


@unique
class SectionEnum(str, Enum):
    WIRE = "wire"
    AGENDA = "agenda"
    MONITORING = "monitoring"
    NEWS_API = "news_api"

    # Are these next 4 needed?
    MEDIA_RELEASES = "media_releases"
    FACTCHECK = "factcheck"
    AM_NEWS = "am_news"
    MARKET_PLACE = "aapX"
