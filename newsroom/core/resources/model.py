from typing import Annotated, Optional, TypedDict

from bson import ObjectId

from superdesk.core.resources import ResourceModelWithObjectId, default_model_config
from superdesk.core.resources.validators import validate_data_relation_async
from superdesk.core.resources.fields import ObjectId as ObjectIdField


# Use strict models for Newshub resources (except for Agenda & Wire)
model_config = default_model_config.copy()
model_config["extra"] = "forbid"


class NewshubResourceModel(ResourceModelWithObjectId):
    model_config = model_config
    original_creator: Annotated[Optional[ObjectIdField], validate_data_relation_async("users")] = None
    version_creator: Annotated[Optional[ObjectIdField], validate_data_relation_async("users")] = None


class BaseNewshubResourceDict(TypedDict):
    _id: ObjectId


class NewshubResourceDict(BaseNewshubResourceDict, total=False):
    original_creator: ObjectId | None
    version_creator: ObjectId | None
