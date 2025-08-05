from typing import Sequence, Any, cast

from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from quart_babel import gettext

from superdesk.core.types import Request, Response
from superdesk.core.module import SuperdeskAsyncApp
from superdesk.core.resources import (
    ResourceConfig,
    MongoIndexOptions,
    MongoResourceConfig,
    RestEndpointConfig,
    RestParentLink,
)
from superdesk.core.web import ItemRequestViewArgs

from newsroom import MONGO_PREFIX
from newsroom.types import (
    TopicFolderResourceModel,
    UserTopicFoldersResourceModel,
    CompanyTopicFoldersResourceModel,
    UserResourceModel,
)
from newsroom.auth import auth_rules
from newsroom.core.resources import NewshubAsyncResourceService, raise_custom_validation_error
from newsroom.topics.topics_async import TopicService
from newsroom.signals import user_deleted


from superdesk.core.resources import ResourceRestEndpoints


class FolderRestEndpoints(ResourceRestEndpoints):
    def _format_error_to_newshub_style(self, response_body: dict) -> dict:
        # Hack to provide Newshub style errors from REST Endpoints API
        # Only needed for TopicFolders - most APIs in Newshub use Endpoints and ResourceServices directly
        # TODO-ASYNC: Provide a better way for the App to handle validation level errors from Web REST APIs

        if response_body.get("_status") == "ERR" and response_body.get("_issues"):
            # Converts
            # {"_issues": {"name": {"name": "Name must be unique"}}}
            # to
            # {"name": "Name must be unique"}
            return {
                field: list(field_error.values())[0]
                for field, field_error in response_body["_issues"].items()
                if len(field_error.values())
            }

        return response_body

    async def create_item(self, request: Request) -> Response:
        """Processes a create item request"""
        response = await super().create_item(request)
        response.body = self._format_error_to_newshub_style(cast(dict, response.body))
        return response

    async def update_item(
        self,
        args: ItemRequestViewArgs,
        params: None,
        request: Request,
    ) -> Response:
        """Processes an update item request"""
        response = await super().update_item(args, params, request)
        response.body = self._format_error_to_newshub_style(cast(dict, response.body))
        return response


class FolderResourceService(NewshubAsyncResourceService[TopicFolderResourceModel]):
    async def create(self, docs: Sequence[TopicFolderResourceModel | dict[str, Any]]) -> list[TopicFolderResourceModel]:
        try:
            return await super().create(docs)
        except DuplicateKeyError:
            raise_custom_validation_error(TopicFolderResourceModel.__name__, "name", gettext("Name must be unique"), "")

    async def update(
        self,
        item_id: str | ObjectId,
        updates: dict[str, Any],
        etag: str | None = None,
        original: TopicFolderResourceModel | None = None,
    ) -> TopicFolderResourceModel:
        try:
            return await super().update(item_id, updates, etag, original)
        except DuplicateKeyError:
            raise_custom_validation_error(TopicFolderResourceModel.__name__, "name", gettext("Name must be unique"), "")

    async def on_deleted(self, doc):
        await self.delete_many(lookup={"parent": doc.id})
        await TopicService().delete_many(lookup={"folder": doc.id})


async def delete_folders_on_user_deleted(user: UserResourceModel) -> None:
    await FolderResourceService().delete_many({"user": user.id})


def init_module(_app: SuperdeskAsyncApp) -> None:
    user_deleted.connect(delete_folders_on_user_deleted)


topic_folders_resource_config = ResourceConfig(
    name="topic_folders",
    data_class=TopicFolderResourceModel,
    service=FolderResourceService,
    mongo=MongoResourceConfig(
        prefix=MONGO_PREFIX,
        indexes=[
            MongoIndexOptions(
                name="unique_topic_folder_name",
                keys=[("company", 1), ("user", 1), ("section", 1), ("parent", 1), ("name", 1)],
                unique=True,
                collation={"locale": "en", "strength": 2},
            )
        ],
    ),
)


class UserFoldersResourceService(FolderResourceService):
    pass


user_topic_folders_resource_config = ResourceConfig(
    name="user_topic_folders",
    data_class=UserTopicFoldersResourceModel,
    service=UserFoldersResourceService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    datasource_name="topic_folders",
    rest_endpoints=RestEndpointConfig(
        endpoints_class=FolderRestEndpoints,
        parent_links=[RestParentLink(resource_name="users", model_id_field="user")],
        url="topic_folders",
        auth=[auth_rules.any_user_role],
    ),
)


class CompanyFoldersResourceService(FolderResourceService):
    pass


company_topic_folder_resource_config = ResourceConfig(
    name="company_topic_folders",
    data_class=CompanyTopicFoldersResourceModel,
    service=CompanyFoldersResourceService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    datasource_name="topic_folders",
    rest_endpoints=RestEndpointConfig(
        endpoints_class=FolderRestEndpoints,
        parent_links=[RestParentLink(resource_name="companies", model_id_field="company")],
        url="topic_folders",
        auth=[auth_rules.any_user_role],
    ),
)
