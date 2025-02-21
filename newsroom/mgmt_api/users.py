import re
import json
from typing import Any, List, Dict
from typing_extensions import override
from bson.objectid import ObjectId

from newsroom import MONGO_PREFIX
from newsroom.core import get_current_wsgi_app
from newsroom.mgmt_api.utils import validate_product_refs
from newsroom.users.service import UsersService
from newsroom.types import UserResourceModel

from superdesk.core.module import Module
from superdesk.core.resources import (
    ResourceConfig,
    MongoResourceConfig,
    RestEndpointConfig,
)
from superdesk.core.types import Request
from superdesk.core.resources.cursor import ElasticsearchResourceCursorAsync, MongoResourceCursorAsync


class CPUsersService(UsersService):
    @override
    async def on_create(self, docs: List[UserResourceModel]) -> None:
        await super().on_create(docs)
        for doc in docs:
            if doc.company:
                doc.company = ObjectId(doc.company)
            if doc.products:
                doc.products = await validate_product_refs(doc.products)

    @override
    async def on_update(self, updates: Dict[str, Any], original: UserResourceModel) -> None:
        if updates.get("products"):
            updates["products"] = await validate_product_refs(updates["products"])
        # Skipping UsersService.on_update as its validations are not needed for this API.
        await super(UsersService, self).on_update(updates, original)

    @override
    async def on_updated(self, updates: Dict[str, Any], original: UserResourceModel) -> None:
        # Skipping UsersService.on_updated as its validations are not needed for this API.
        await super(UsersService, self).on_updated(updates, original)

    @override
    async def on_delete(self, doc: UserResourceModel) -> None:
        get_current_wsgi_app().cache.delete(str(doc.id))

    async def find(
        self, req: Request
    ) -> ElasticsearchResourceCursorAsync[UserResourceModel] | MongoResourceCursorAsync[UserResourceModel]:
        where = json.loads(req.where or "{}") if isinstance(req.where, str) else req.where or {}
        if "email" in where:
            where["email"] = {"$regex": re.compile("^{}$".format(re.escape(where["email"])), re.IGNORECASE)}
        req.where = where
        return await super().find(req)


users_resource_config = ResourceConfig(
    name="users",
    data_class=UserResourceModel,
    service=CPUsersService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    rest_endpoints=RestEndpointConfig(),
)

module = Module(
    name="newsroom.mgmt_api.users",
    resources=[users_resource_config],
)
