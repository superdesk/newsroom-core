from copy import deepcopy

import superdesk

from content_api.items.resource import ItemsResource as BaseItemsResource
from content_api.items.service import ItemsService as BaseItemsService

from content_api.items_versions.resource import ItemsVersionsResource as BaseItemsVersionsResource
from content_api.items_versions.service import ItemsVersionsService

from superdesk.metadata.item import metadata_schema


class ItemsResource(BaseItemsResource):
    schema = deepcopy(BaseItemsResource.schema)
    schema["slugline"] = schema["headline"] = schema["body_html"] = schema["description_html"] = metadata_schema[
        "body_html"
    ].copy()
    schema["expiry"] = {"type": "datetime", "reaonly": True}


class ItemsService(BaseItemsService):
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
