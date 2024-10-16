from typing import Annotated, Any
from datetime import datetime

from superdesk.core.resources.fields import ObjectId as ObjectIdField, Keyword
from superdesk.core.resources.validators import validate_data_relation_async

from newsroom.core.resources.model import NewshubResourceModel


class HistoryResourceModel(NewshubResourceModel):
    action: Keyword
    versioncreated: datetime
    user: Annotated[ObjectIdField | None, validate_data_relation_async("users")] = None
    company: Annotated[ObjectIdField | None, validate_data_relation_async("companies")] = None
    item: Keyword
    version: str
    section: Keyword
    extra_data: dict[str, Any] | None = None
