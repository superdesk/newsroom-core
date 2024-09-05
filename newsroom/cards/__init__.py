import superdesk
from flask import Blueprint
from flask_babel import lazy_gettext
from typing_extensions import assert_never

from newsroom.types import DashboardCardType

from .cards import CardsResource, CardsService

blueprint = Blueprint("cards", __name__)


def get_card_size(cardType: DashboardCardType) -> int:
    if cardType == "1x1-top-news":
        return 1
    if cardType == "2x2-events":
        return 4
    if cardType == "2x2-top-news":
        return 4
    if cardType == "3-picture-text":
        return 3
    if cardType == "3-text-only":
        return 3
    if cardType == "4-media-gallery":
        return 4
    if cardType == "4-photo-gallery":
        return 4
    if cardType == "4-picture-text":
        return 4
    if cardType == "4-text-only":
        return 4
    if cardType == "6-navigation-row":
        return 6
    if cardType == "6-text-only":
        return 6
    if cardType == "wire-list":
        return 5
    assert_never(cardType)


def get_card_type(cardType: str) -> DashboardCardType:
    if cardType == "1x1-top-news":
        return "1x1-top-news"
    if cardType == "2x2-events":
        return "2x2-events"
    if cardType == "2x2-top-news":
        return "2x2-top-news"
    if cardType == "3-picture-text":
        return "3-picture-text"
    if cardType == "3-text-only":
        return "3-text-only"
    if cardType == "4-media-gallery":
        return "4-media-gallery"
    if cardType == "4-photo-gallery":
        return "4-photo-gallery"
    if cardType == "4-picture-text":
        return "4-picture-text"
    if cardType == "4-text-only":
        return "4-text-only"
    if cardType == "6-navigation-row":
        return "6-navigation-row"
    if cardType == "6-text-only":
        return "6-text-only"
    if cardType == "wire-list":
        return "wire-list"
    raise ValueError(f"Invalid card type: {cardType}")


def init_app(app):
    from . import views  # noqa

    superdesk.register_resource("cards", CardsResource, CardsService, _app=app)
    app.settings_app("cards", lazy_gettext("Dashboards"), weight=500, data=views.get_settings_data)
