from typing import List, Dict
from typing_extensions import assert_never
from copy import deepcopy

from flask import current_app as app
from bson import ObjectId
import superdesk

from content_api.items.resource import ItemsResource as BaseItemsResource
from content_api.items.service import ItemsService as BaseItemsService

from content_api.items_versions.resource import ItemsVersionsResource as BaseItemsVersionsResource
from content_api.items_versions.service import ItemsVersionsService

from superdesk.metadata.item import metadata_schema

from newsroom.types import DashboardCard, Article


class ItemsResource(BaseItemsResource):
    schema = deepcopy(BaseItemsResource.schema)
    schema["slugline"] = schema["headline"] = schema["body_html"] = schema["description_html"] = metadata_schema[
        "body_html"
    ].copy()

    schema["expiry"] = {"type": "datetime"}

    mongo_indexes = deepcopy(BaseItemsResource.mongo_indexes) or {}
    mongo_indexes.update(
        {
            "evolvedfrom_1": ([("evelovedfrom", 1)], {"background": True}),
        }
    )


class ItemsService(BaseItemsService):
    def _is_internal_api(self):
        # we need to avoid superdesk core handling which makes it return nothing
        # todo: get rid of the base item service from content api, there is too much
        # logic related to subscribers
        return False

    def get_expired_items(self, expiry_datetime=None, expiry_days=None, max_results=None, include_children=True):
        # remove old items based on expiry days config
        for items in super().get_expired_items(expiry_datetime, expiry_days, max_results, include_children):
            yield items
        # remove items with custom expiry
        lookup = {"expiry": {"$lt": expiry_datetime}}
        if max_results is None:
            max_results = 100
        for item in self.get_all_batch(max_results, 100, lookup):
            yield [item]


class ItemsVersionsResource(BaseItemsVersionsResource):
    schema = deepcopy(BaseItemsVersionsResource.schema)
    schema["slugline"] = schema["headline"] = schema["body_html"] = schema["description_html"] = metadata_schema[
        "body_html"
    ].copy()


def init_app(app):
    superdesk.register_resource("items", ItemsResource, ItemsService, _app=app)
    superdesk.register_resource("items_versions", ItemsVersionsResource, ItemsVersionsService, _app=app)


def get_items_for_dashboard(
    cards: List[DashboardCard], exclude_embargoed: bool = False, filter_public_fields: bool = False
) -> Dict[str, List[Article]]:
    """Get dictionary of ``card.label`` to list of ``Article`` for the provided cards

    :param cards: List of cards to get items for
    :param exclude_embargoed: If ``True``, will exclude embargoed items
    :param filter_public_fields: If ``True``, will remove fields from items that are not in the
    ``PUBLIC_WIRE_ALLOWED_FIELDS`` config
    """

    allowed_public_fields = app.config.get("PUBLIC_WIRE_ALLOWED_FIELDS", [])

    if len(allowed_public_fields) == 0:
        filter_public_fields = False

    def filter_fields(item: Article) -> Article:
        for field in list(item.keys()):
            if field == "associations":
                for association in item[field].values():
                    filter_fields(association)
            elif field not in allowed_public_fields:
                item.pop(field, None)
        return item

    items_by_card = {}
    for card in cards:
        if card["config"].get("product"):
            items_by_card[card["label"]] = [
                filter_fields(item) if filter_public_fields else item
                for item in superdesk.get_resource_service("wire_search").get_product_items(
                    ObjectId(card["config"]["product"]),
                    card["config"]["size"] or get_default_size(card),
                    exclude_embargoed=exclude_embargoed,
                )
            ]
        elif card["type"] == "4-photo-gallery":
            # Omit external media, let the client manually request these
            # using '/media_card_external' endpoint
            items_by_card[card["label"]] = []

    return items_by_card


def get_default_size(card: DashboardCard) -> int:
    if not card.get("type"):
        return 0
    if card["type"] == "1x1-top-news":
        return 1
    if card["type"] == "2x2-events":
        return 4
    if card["type"] == "2x2-top-news":
        return 4
    if card["type"] == "3-picture-text":
        return 3
    if card["type"] == "3-text-only":
        return 3
    if card["type"] == "4-media-gallery":
        return 4
    if card["type"] == "4-photo-gallery":
        return 4
    if card["type"] == "4-picture-text":
        return 4
    if card["type"] == "4-text-only":
        return 4
    if card["type"] == "6-navigation-row":
        return 6
    if card["type"] == "6-text-only":
        return 6
    if card["type"] == "wire-list":
        return 5
    assert_never(card["type"])
