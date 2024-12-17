from typing import Sequence, Any

from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from quart_babel import gettext

from superdesk.core.module import SuperdeskAsyncApp
from superdesk.core.resources import (
    ResourceConfig,
    MongoIndexOptions,
    MongoResourceConfig,
    RestEndpointConfig,
    RestParentLink,
)

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


class FolderResourceService(NewshubAsyncResourceService[TopicFolderResourceModel]):
    async def create(self, docs: Sequence[TopicFolderResourceModel | dict[str, Any]]) -> list[str]:
        try:
            return await super().create(docs)
        except DuplicateKeyError:
            raise_custom_validation_error(TopicFolderResourceModel.__name__, "name", gettext("Name must be unique"), "")

    async def update(self, item_id: str | ObjectId, updates: dict[str, Any], etag: str | None = None) -> None:
        try:
            await super().update(item_id, updates, etag)
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
        parent_links=[RestParentLink(resource_name="companies", model_id_field="company")],
        url="topic_folders",
        auth=[auth_rules.any_user_role],
    ),
)
