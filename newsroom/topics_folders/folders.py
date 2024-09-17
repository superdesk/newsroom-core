from enum import Enum, unique
from typing import Optional, Annotated

from newsroom import MONGO_PREFIX
from newsroom.core.resources.model import NewshubResourceModel
from newsroom.core.resources.service import NewshubAsyncResourceService

from newsroom.topics.topics_async import TopicService

from superdesk.core.web import EndpointGroup
from superdesk.core.resources.fields import ObjectId as ObjectIdField
from superdesk.core.resources import (
    ResourceConfig,
    MongoIndexOptions,
    MongoResourceConfig,
    RestEndpointConfig,
    RestParentLink,
)
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
    rest_endpoints=RestEndpointConfig(parent_links=[RestParentLink(resource_name="users", model_id_field="user")]),
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
        parent_links=[RestParentLink(resource_name="companies", model_id_field="company")]
    ),
)
