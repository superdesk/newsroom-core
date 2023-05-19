from copy import deepcopy

import superdesk
from content_api.items.resource import ItemsResource as BaseItemsResource
from content_api.items.service import ItemsService

from content_api.items_versions.resource import ItemsVersionsResource as BaseItemsVersionsResource
from content_api.items_versions.service import ItemsVersionsService


class ItemsResource(BaseItemsResource):
    schema = deepcopy(BaseItemsResource.schema)
    schema["slugline"] = schema["headline"] = schema["body_html"]


class ItemsVersionsResource(BaseItemsVersionsResource):
    schema = deepcopy(BaseItemsVersionsResource.schema)
    schema["slugline"] = schema["headline"] = schema["body_html"]


def init_app(app):
    superdesk.register_resource("items", ItemsResource, ItemsService, _app=app)
    superdesk.register_resource("items_versions", ItemsVersionsResource, ItemsVersionsService, _app=app)
