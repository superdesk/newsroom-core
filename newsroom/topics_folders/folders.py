from enum import Enum, unique
from typing import Optional, Annotated

from newsroom import MONGO_PREFIX
from newsroom.core.resources.model import NewshubResourceModel
from newsroom.core.resources.service import NewshubAsyncResourceService

# from newsroom.signals import user_deleted

from newsroom.topics.topics_async import TopicService

from superdesk.core.resources.fields import ObjectId as ObjectIdField
from superdesk.core.resources import (
    ResourceConfig,
    MongoIndexOptions,
    MongoResourceConfig,
    RestEndpointConfig,
    RestParentLink,
)
from superdesk.core.resources.validators import validate_data_relation_async

# from superdesk.core.module import SuperdeskAsyncApp


@unique
class SectionType(str, Enum):
    WIRE = "wire"
    AGENDA = "agenda"
    MONITORING = "monitoring"


class FolderResourceModel(NewshubResourceModel):
    name: str
    parent: Annotated[Optional[ObjectIdField], validate_data_relation_async("topic_folders")] = None
    section: SectionType


class FolderResourceService(NewshubAsyncResourceService[FolderResourceModel]):
    async def on_deleted(self, doc):
        await self.delete({"parent": doc["_id"]})
        await TopicService().delete({"folder": doc["_id"]})

    async def on_user_deleted(self, sender, user, **kwargs):
        await self.delete({"user": user["_id"]})


# TODO:Async, need to wait for SDESK-7376

# async def init(app: SuperdeskAsyncApp):
#     user_deleted.connect(await FolderResourceService().on_user_deleted)  # type: ignore


topic_folders_resource_config = ResourceConfig(
    name="topic_folders",
    data_class=FolderResourceModel,
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


class UserFoldersResourceModel(FolderResourceModel):
    """
    User Based FolderResource Model
    """

    user: Annotated[ObjectIdField, validate_data_relation_async("users")]


class UserFoldersResourceService(NewshubAsyncResourceService[UserFoldersResourceModel]):
    pass


user_topic_folders_resource_config = ResourceConfig(
    name="user_topic_folders",
    data_class=UserFoldersResourceModel,
    service=UserFoldersResourceService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    datasource_name="topic_folders",
    rest_endpoints=RestEndpointConfig(
        parent_links=[RestParentLink(resource_name="users", model_id_field="user")], url="topic_folders"
    ),
)


class CompanyFoldersResourceModel(FolderResourceModel):
    """
    Company Based FolderResource Model
    """

    company: Annotated[ObjectIdField, validate_data_relation_async("companies")]


class CompanyFoldersResourceService(NewshubAsyncResourceService[CompanyFoldersResourceModel]):
    resource_name = "company_topic_folders"


company_topic_folder_resource_config = ResourceConfig(
    name="company_topic_folders",
    data_class=CompanyFoldersResourceModel,
    service=CompanyFoldersResourceService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    datasource_name="topic_folders",
    rest_endpoints=RestEndpointConfig(
        parent_links=[RestParentLink(resource_name="companies", model_id_field="company")], url="topic_folders"
    ),
)
