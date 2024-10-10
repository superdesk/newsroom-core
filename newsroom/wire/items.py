from typing import List, Dict
from copy import deepcopy

from bson import ObjectId

from superdesk.core import get_app_config
import superdesk

from content_api.items.resource import ItemsResource as BaseItemsResource
from content_api.items.service import ItemsService as BaseItemsService

from content_api.items_versions.resource import ItemsVersionsResource as BaseItemsVersionsResource
from content_api.items_versions.service import ItemsVersionsService

from superdesk.metadata.item import metadata_schema

from newsroom.types import Article, DashboardCardDict
from newsroom.cards import get_card_size


class ItemsResource(BaseItemsResource):
    schema = deepcopy(BaseItemsResource.schema)
    schema["slugline"] = schema["headline"] = schema["body_html"] = schema["description_html"] = metadata_schema[
        "body_html"
    ].copy()
    schema["urgency"] = {**metadata_schema["urgency"], "mapping": {"type": "keyword"}}
    schema["priority"] = {**metadata_schema["priority"], "mapping": {"type": "keyword"}}

    schema["expiry"] = {"type": "datetime"}

    mongo_indexes = deepcopy(BaseItemsResource.mongo_indexes) or {}
    mongo_indexes.update(
        {
            "evolvedfrom_1": ([("evolvedfrom", 1)], {"background": True}),
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
    schema["urgency"] = {**metadata_schema["urgency"], "mapping": {"type": "keyword"}}
    schema["priority"] = {**metadata_schema["priority"], "mapping": {"type": "keyword"}}


def init_app(app):
    superdesk.register_resource("items", ItemsResource, ItemsService, _app=app)
    superdesk.register_resource("items_versions", ItemsVersionsResource, ItemsVersionsService, _app=app)


def get_items_for_dashboard(
    cards: List[DashboardCardDict], exclude_embargoed: bool = False, filter_public_fields: bool = False
) -> Dict[str, List[Article]]:
    """Get dictionary of ``card.label`` to list of ``Article`` for the provided cards

    :param cards: List of cards to get items for
    :param exclude_embargoed: If ``True``, will exclude embargoed items
    :param filter_public_fields: If ``True``, will remove fields from items that are not in the
    ``PUBLIC_WIRE_ALLOWED_FIELDS`` config
    """

    allowed_public_fields = get_app_config("PUBLIC_WIRE_ALLOWED_FIELDS", [])

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
                    ObjectId(card["config"].get("product")),
                    card["config"].get("size") or get_card_size(card["type"]),
                    exclude_embargoed=exclude_embargoed,
                )
            ]
        elif card["type"] == "4-photo-gallery":
            # Omit external media, let the client manually request these
            # using '/media_card_external' endpoint
            items_by_card[card["label"]] = []

    return items_by_card
