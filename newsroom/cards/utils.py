from typing_extensions import assert_never

from .model import DashboardCardType


def get_card_size(cardType: DashboardCardType) -> int:
    if cardType == DashboardCardType.TOP_NEWS_1x1:
        return 1
    if cardType == DashboardCardType.EVENTS_2x2:
        return 4
    if cardType == DashboardCardType.TOP_NEWS_2x2:
        return 4
    if cardType == DashboardCardType.PIC_TEXT_3:
        return 3
    if cardType == DashboardCardType.TEXT_3:
        return 3
    if cardType == DashboardCardType.MEDIA_GALLERY_4:
        return 4
    if cardType == DashboardCardType.PHOTO_GALLERY_4:
        return 4
    if cardType == DashboardCardType.PIC_TEXT_4:
        return 4
    if cardType == DashboardCardType.TEXT_4:
        return 4
    if cardType == DashboardCardType.NAV_ROW_6:
        return 6
    if cardType == DashboardCardType.TEXT_6:
        return 6
    if cardType == DashboardCardType.WIRE_LIST:
        return 5
    assert_never(cardType)


def get_card_type(cardType: str) -> DashboardCardType:
    if cardType == "1x1-top-news":
        return DashboardCardType.TOP_NEWS_1x1
    if cardType == "2x2-events":
        return DashboardCardType.EVENTS_2x2
    if cardType == "2x2-top-news":
        return DashboardCardType.TOP_NEWS_2x2
    if cardType == "3-picture-text":
        return DashboardCardType.PIC_TEXT_3
    if cardType == "3-text-only":
        return DashboardCardType.TEXT_3
    if cardType == "4-media-gallery":
        return DashboardCardType.MEDIA_GALLERY_4
    if cardType == "4-photo-gallery":
        return DashboardCardType.PHOTO_GALLERY_4
    if cardType == "4-picture-text":
        return DashboardCardType.PIC_TEXT_4
    if cardType == "4-text-only":
        return DashboardCardType.TEXT_4
    if cardType == "6-navigation-row":
        return DashboardCardType.NAV_ROW_6
    if cardType == "6-text-only":
        return DashboardCardType.TEXT_6
    if cardType == "wire-list":
        return DashboardCardType.WIRE_LIST
    raise ValueError(f"Invalid card type: {cardType}")
