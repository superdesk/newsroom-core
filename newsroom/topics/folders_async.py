from enum import Enum, unique
from typing import Optional, Annotated

from newsroom import MONGO_PREFIX
from newsroom.core.resources.model import NewshubResourceModel
from newsroom.core.resources.service import NewshubAsyncResourceService

from .topics_async import TopicService

from superdesk.core.web import EndpointGroup
from superdesk.core.resources.fields import ObjectId as ObjectIdField
from superdesk.core.resources import ResourceConfig, MongoIndexOptions, MongoResourceConfig
from superdesk.core.resources.validators import validate_data_relation_async


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
    resource_name = "topic_folders"

    async def on_deleted(self, doc):
        await self.delete({"parent": doc["_id"]})
        await TopicService().delete({"folder": doc["_id"]})

    async def on_user_deleted(self, sender, user, **kwargs):
        await self.delete({"user": user["_id"]})


folder_resource_config = ResourceConfig(
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

topic_folders_endpoints = EndpointGroup("topic_folders", __name__)


class UserFoldersResourceModel(FolderResourceModel):
    """
    User Based FolderResource Model
    """

    user: Annotated[ObjectIdField, validate_data_relation_async("users")]


class UserFoldersResourceService(NewshubAsyncResourceService[UserFoldersResourceModel]):
    resource_name = "user_topic_folders"
    pass


user_topic_folders_resource_config = ResourceConfig(
    name="user_topic_folders",
    data_class=FolderResourceModel,
    service=FolderResourceService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
)


class CompanyFoldersResourceModel(FolderResourceModel):
    """
    Company Based FolderResource Model
    """

    company: Annotated[ObjectIdField, validate_data_relation_async("companies")]


class CompanyFoldersResourceService(NewshubAsyncResourceService[UserFoldersResourceModel]):
    resource_name = "company_topic_folders"
    pass


company_topic_folder_resource_config = ResourceConfig(
    name="company_topic_folders",
    data_class=FolderResourceModel,
    service=FolderResourceService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
)
