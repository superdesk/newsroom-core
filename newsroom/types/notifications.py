from datetime import datetime
from typing import Annotated
from pydantic import Field

from superdesk.core.resources import ResourceModel, dataclass
from superdesk.core.resources.fields import ObjectId
from superdesk.core.resources.validators import validate_data_relation_async


user_validated_type = Annotated[ObjectId, validate_data_relation_async("users")]


class Notification(ResourceModel):
    # item needs to be str | ObjectId as resource can be topic, agenda items, items
    # and potentially other types of resources
    item: str | ObjectId
    resource: str

    user: user_validated_type
    action: str
    data: dict = Field(default_factory=dict)


@dataclass
class NotificationTopic:
    topic_id: Annotated[ObjectId, validate_data_relation_async("topics")]
    last_item_arrived: datetime
    section: str
    items: list[str | ObjectId] = Field(default_factory=list)


class NotificationQueue(ResourceModel):
    user: user_validated_type
    topics: list[NotificationTopic]
