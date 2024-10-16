from enum import Enum, unique
from pydantic import Field
from typing import Any, Annotated

from newsroom.core.resources.model import NewshubResourceModel
from superdesk.core.resources import dataclass

from superdesk.core.resources.fields import ObjectId as ObjectIdField
from superdesk.core.resources.validators import validate_data_relation_async


@unique
class NotificationType(str, Enum):
    NONE = "none"
    REAL_TIME = "real-time"
    SCHEDULED = "scheduled"


@unique
class TopicType(str, Enum):
    WIRE = "wire"
    AGENDA = "agenda"


@dataclass
class TopicSubscriberModel:
    user_id: Annotated[ObjectIdField, validate_data_relation_async("users")]
    notification_type: NotificationType = NotificationType.REAL_TIME


class TopicResourceModel(NewshubResourceModel):
    label: str
    query: str | None = None
    filter: dict[str, Any] | None = None
    created_filter: Annotated[dict[str, Any] | None, Field(alias="created")] = None
    user: Annotated[ObjectIdField | None, validate_data_relation_async("users")] = None
    company: Annotated[ObjectIdField | None, validate_data_relation_async("companies")] = None
    is_global: bool = False
    subscribers: list[TopicSubscriberModel] = Field(default_factory=list)
    timezone_offset: int | None = None
    topic_type: TopicType
    navigation: Annotated[list[ObjectIdField] | None, validate_data_relation_async("navigations")] = None
    folder: Annotated[ObjectIdField | None, validate_data_relation_async("topic_folders")] = None
    advanced: dict[str, Any] | None = None


@unique
class SectionType(str, Enum):
    WIRE = "wire"
    AGENDA = "agenda"
    MONITORING = "monitoring"


class TopicFolderResourceModel(NewshubResourceModel):
    name: str
    parent: Annotated[ObjectIdField | None, validate_data_relation_async("topic_folders")] = None
    section: SectionType


class UserTopicFoldersResourceModel(TopicFolderResourceModel):
    """
    User Based FolderResource Model
    """

    user: Annotated[ObjectIdField, validate_data_relation_async("users")]


class CompanyTopicFoldersResourceModel(TopicFolderResourceModel):
    """
    Company Based FolderResource Model
    """

    company: Annotated[ObjectIdField, validate_data_relation_async("companies")]
