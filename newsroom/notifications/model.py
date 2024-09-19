from typing import Annotated, Optional
from superdesk.core.resources import ResourceModel
from superdesk.core.resources.fields import ObjectId
from superdesk.core.resources.validators import validate_data_relation_async
from newsroom.users.module import users_resource_config


class Notification(ResourceModel):
    item: str | ObjectId
    # TODO-async: replace the one above with the one below once `items` are migrated to async framework
    # item: Annotated[Optional[ObjectId], validate_data_relation_async("items")] = None

    user: Annotated[ObjectId, validate_data_relation_async(users_resource_config.name)]
    resource: Optional[str] = ""
    action: Optional[str] = ""
    data: Optional[dict] = {}
