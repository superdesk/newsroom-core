from typing import Annotated
from typing_extensions import TypedDict
from enum import Enum, unique

from pydantic import Field, StringConstraints

from newsroom.core.resources import NewshubResourceModel, NewshubResourceDict
from newsroom.core.resources.validators import validate_supported_dashboard


@unique
class DashboardCardType(str, Enum):
    TEXT_3 = "3-text-only"
    TEXT_4 = "4-text-only"
    TEXT_6 = "6-text-only"

    PIC_TEXT_3 = "3-picture-text"
    PIC_TEXT_4 = "4-picture-text"

    MEDIA_GALLERY_4 = "4-media-gallery"
    PHOTO_GALLERY_4 = "4-photo-gallery"

    TOP_NEWS_1x1 = "1x1-top-news"
    TOP_NEWS_2x2 = "2x2-top-news"

    EVENTS_2x2 = "2x2-events"
    NAV_ROW_6 = "6-navigation-row"
    WIRE_LIST = "wire-list"


class DashboardCardConfig(TypedDict, total=False):
    product: str
    size: int
    events: dict
    sources: list[dict]


class CardResourceModel(NewshubResourceModel):
    label: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    dashboard_type: Annotated[DashboardCardType, Field(alias="type")]
    dashboard: Annotated[str, validate_supported_dashboard()] = "newsroom"
    config: DashboardCardConfig | None = None
    order: int = 0


class BaseDashboardCardDict(NewshubResourceDict):
    label: str
    type: DashboardCardType


class DashboardCardDict(BaseDashboardCardDict, total=False):
    dashboard: str
    config: DashboardCardConfig
    order: int
