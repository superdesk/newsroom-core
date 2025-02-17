from bson.objectid import ObjectId
from flask import current_app as app
from newsroom.users.service import UsersService
from newsroom.types import UserResourceModel
from superdesk.errors import SuperdeskApiError
from typing_extensions import override

from newsroom.mgmt_api.utils import validate_product_refs
from superdesk.core.resources import ResourceConfig, MongoResourceConfig, RestEndpointConfig
from content_api import MONGO_PREFIX
from superdesk.core.module import Module
from typing import Any
from newsroom.core import get_current_wsgi_app


class CPUsersResource(UserResourceModel):
    pass


class CPUsersService(UsersService):
    @override
    async def on_create(self, docs):
        await super().on_create(docs)
        for doc in docs:
            if doc.user_type != "administrator" and not doc.company:
                message = "Company is required if user type is not administrator."
                raise SuperdeskApiError.badRequestError(message=message, payload=message)
            locale = doc.locale
            if locale and locale not in app.config["LANGUAGES"]:
                message = "Locale is not in configured list of locales."
                raise SuperdeskApiError.badRequestError(message=message, payload=message)
            if doc.company:
                doc.company = ObjectId(doc.company)
            if doc.products:
                doc.products = await validate_product_refs(doc.products)

    @override
    async def on_update(self, updates: dict[str, Any], original: UserResourceModel):
        if updates.get("products"):
            updates["products"] = await validate_product_refs(updates["products"])

    @override
    async def on_updated(self, updates: dict[str, Any], original: UserResourceModel):
        pass

    @override
    async def on_delete(self, doc):
        app = get_current_wsgi_app()
        app.cache.delete(str(doc.id))


users_resource_config = ResourceConfig(
    name="users",
    data_class=CPUsersResource,
    service=CPUsersService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    rest_endpoints=RestEndpointConfig(auth=False),
)

module = Module(
    name="newsroom.mgmt_api.users",
    resources=[users_resource_config],
)
