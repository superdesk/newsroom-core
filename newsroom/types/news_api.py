from typing import Annotated
from datetime import datetime

from pydantic import Field

from superdesk.core.resources import fields
from superdesk.utc import utcnow

from newsroom.core.resources import NewshubResourceModel


class NewsApiAuditResourceModel(NewshubResourceModel):
    uri: fields.Keyword
    remote_addr: fields.Keyword
    endpoint: fields.Keyword
    items_id: Annotated[list[str], fields.keyword_mapping()]
    created: datetime = Field(default_factory=utcnow)
    subscriber: fields.ObjectId | None = None
