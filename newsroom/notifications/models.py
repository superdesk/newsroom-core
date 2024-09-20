from datetime import datetime
from dataclasses import dataclass
from typing import Annotated, Optional
from superdesk.core.resources import ResourceModel
from superdesk.core.resources.fields import ObjectId, Field
from superdesk.core.resources.validators import validate_data_relation_async
from newsroom.users.module import users_resource_config


user_validated_type = Annotated[ObjectId, validate_data_relation_async(users_resource_config.name)]


class Notification(ResourceModel):
    item: str | ObjectId
    # TODO-async: replace the one above with the one below once `items` are migrated to async framework
    # item: Annotated[Optional[ObjectId], validate_data_relation_async("items")] = None

    user: user_validated_type
    resource: Optional[str] = ""
    action: Optional[str] = ""
    data: Optional[dict] = {}


@dataclass
class Topic:
    topic_id: ObjectId
    last_item_arrived: datetime
    section: str
    items: list[Annotated[ObjectId, validate_data_relation_async("items")]] = Field(default_factory=list)


class NotificationQueue(ResourceModel):
    user: user_validated_type
    topics: list[Topic]
