# from superdesk.core.module import SuperdeskAsyncApp
from superdesk.core.resources import (
    ResourceConfig,
    MongoIndexOptions,
    MongoResourceConfig,
    RestEndpointConfig,
    RestParentLink,
)

from newsroom import MONGO_PREFIX
from newsroom.types import TopicFolderResourceModel, UserTopicFoldersResourceModel, CompanyTopicFoldersResourceModel
from newsroom.auth import auth_rules
from newsroom.core.resources import NewshubAsyncResourceService
from newsroom.topics.topics_async import TopicService

# from newsroom.signals import user_deleted


class FolderResourceService(NewshubAsyncResourceService[TopicFolderResourceModel]):
    async def on_deleted(self, doc):
        await self.delete_many(lookup={"parent": doc.id})
        await TopicService().delete_many(lookup={"folder": doc.id})

    async def on_user_deleted(self, sender, user, **kwargs):
        await self.delete_many(lookup={"user": user["_id"]})


# TODO-ASYNC, need to wait for SDESK-7376

# async def init(app: SuperdeskAsyncApp):
#     user_deleted.connect(await FolderResourceService().on_user_deleted)  # type: ignore


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
