from bson.objectid import ObjectId
from pymongo.collation import Collation
from flask import current_app as app
from newsroom.users.service import UsersService
from newsroom.types import UserResourceModel
from superdesk.errors import SuperdeskApiError
from typing_extensions import override

from newsroom.mgmt_api.utils import validate_product_refs
from superdesk.core.resources import ResourceConfig, MongoResourceConfig
from content_api import MONGO_PREFIX
from superdesk.core.web import EndpointGroup
from superdesk.core.module import Module


class CPUsersResource(UserResourceModel):
    pass


class CPUsersService(UsersService):
    @override
    async def check_permissions(self, doc, updates=None):
        """Avoid testing if user has permissions."""
        pass

    @override
    async def on_create(self, docs):
        await super().on_create(docs)
        for doc in docs:
            if doc.get("user_type") != "administrator" and not doc.get("company"):
                message = "Company is required if user type is not administrator."
                raise SuperdeskApiError.badRequestError(message=message, payload=message)
            locale = doc.get("locale")
            if locale and locale not in app.config["LANGUAGES"]:
                message = "Locale is not in configured list of locales."
                raise SuperdeskApiError.badRequestError(message=message, payload=message)
            if doc.get("company"):
                doc["company"] = ObjectId(doc.get("company"))
            if doc.get("products"):
                await validate_product_refs(doc["products"])

    @override
    async def on_update(self, updates, original):
        if updates.get("products"):
            await validate_product_refs(updates["products"])

    @override
    async def get(self, req, lookup):
        """"""
        cursor = await super().get(req, lookup)
        cursor.collation(Collation(locale="en", strength=1))
        return cursor


users_resource_config = ResourceConfig(
    name="users",
    data_class=CPUsersResource,
    service=CPUsersService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
)

users_endpoints = EndpointGroup("users", __name__)

module = Module(
    name="newsroom.mgmt_api.users",
    resources=[users_resource_config],
    endpoints=[users_endpoints],
)
