from typing import Annotated, Optional

from superdesk.core.resources import ResourceModelWithObjectId
from superdesk.core.resources.validators import validate_data_relation_async
from superdesk.core.resources.fields import ObjectId as ObjectIdField


class NewshubResourceModel(ResourceModelWithObjectId):
    original_creator: Annotated[Optional[ObjectIdField], validate_data_relation_async("users")] = None
    version_creator: Annotated[Optional[ObjectIdField], validate_data_relation_async("users")] = None
