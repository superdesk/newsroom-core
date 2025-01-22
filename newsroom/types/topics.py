from enum import Enum, unique
from pydantic import Field
from typing import Any, Annotated


from superdesk.core.resources import Dataclass
from superdesk.core.resources.fields import ObjectId as ObjectIdField
from superdesk.core.resources.validators import validate_data_relation_async

from newsroom.core.resources.model import NewshubResourceModel

from .common import SectionEnum
from .search import AdvancedSearchParams


@unique
class NotificationType(str, Enum):
    NONE = "none"
    REAL_TIME = "real-time"
    SCHEDULED = "scheduled"


class TopicSubscriberModel(Dataclass):
    user_id: Annotated[ObjectIdField, validate_data_relation_async("users")]
    notification_type: NotificationType = NotificationType.REAL_TIME


class TopicCreatedFilters(Dataclass):
    created_from: Annotated[str | None, Field(alias="from")] = None
    created_to: Annotated[str | None, Field(alias="to")] = None
    date_filter: str | None = None


class TopicResourceModel(NewshubResourceModel):
    label: str
    query: str | None = None
    filter: dict[str, Any] | None = None

    created_filter: Annotated[TopicCreatedFilters | None, Field(alias="created")] = None

    user: Annotated[ObjectIdField | None, validate_data_relation_async("users")] = None
    company: Annotated[ObjectIdField | None, validate_data_relation_async("companies")] = None
    is_global: bool = False
    subscribers: list[TopicSubscriberModel] = Field(default_factory=list)
    timezone_offset: int | None = None
    topic_type: SectionEnum
    navigation: Annotated[list[ObjectIdField] | None, validate_data_relation_async("navigations")] = None
    folder: Annotated[ObjectIdField | None, validate_data_relation_async("topic_folders")] = None
    advanced: AdvancedSearchParams | None = None


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
