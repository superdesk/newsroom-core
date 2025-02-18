from typing import Any, List, Dict
from typing_extensions import override
from bson.objectid import ObjectId
from flask import current_app as app

from newsroom import MONGO_PREFIX
from newsroom.core import get_current_wsgi_app
from newsroom.mgmt_api.utils import validate_product_refs
from newsroom.users.service import UsersService
from newsroom.types import UserResourceModel

from superdesk.core.module import Module
from superdesk.core.resources import ResourceConfig, MongoIndexOptions, MongoResourceConfig, RestEndpointConfig
from superdesk.errors import SuperdeskApiError


class CPUsersResource(UserResourceModel):
    pass


class CPUsersService(UsersService):
    @override
    async def on_create(self, docs: List[UserResourceModel]) -> None:
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
    async def on_update(self, updates: Dict[str, Any], original: UserResourceModel) -> None:
        if updates.get("products"):
            updates["products"] = await validate_product_refs(updates["products"])

    @override
    async def on_updated(self, updates: Dict[str, Any], original: UserResourceModel) -> None:
        pass

    @override
    async def on_delete(self, doc: UserResourceModel) -> None:
        app = get_current_wsgi_app()
        app.cache.delete(str(doc.id))


users_resource_config = ResourceConfig(
    name="users",
    data_class=CPUsersResource,
    service=CPUsersService,
    mongo=MongoResourceConfig(
        prefix=MONGO_PREFIX,
        indexes=[
            MongoIndexOptions(
                name="email",
                keys=[("email", 1)],
                unique=True,
                collation={"locale": "en", "strength": 2},
            ),
        ],
    ),
    rest_endpoints=RestEndpointConfig(auth=False),
)

module = Module(
    name="newsroom.mgmt_api.users",
    resources=[users_resource_config],
)
