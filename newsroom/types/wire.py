from typing import Annotated
from datetime import datetime

from pydantic import Field

from superdesk.core.resources import fields, Dataclass
from content_api.items.model import ContentAPIItem, CVItemWithCode


class PublishedProduct(Dataclass):
    code: fields.Keyword
    name: fields.Keyword | None = None


class WireItem(ContentAPIItem):
    products: Annotated[list[PublishedProduct], Field(default_factory=list)]
    publish_schedule: datetime | None = None

    bookmarks: Annotated[list[fields.ObjectId], fields.keyword_mapping(), Field(default_factory=list)]
    downloads: Annotated[list[fields.ObjectId], fields.keyword_mapping(), Field(default_factory=list)]
    shares: Annotated[list[fields.ObjectId], fields.keyword_mapping(), Field(default_factory=list)]
    prints: Annotated[list[fields.ObjectId], fields.keyword_mapping(), Field(default_factory=list)]
    copies: Annotated[list[fields.ObjectId], fields.keyword_mapping(), Field(default_factory=list)]

    # Overrides from ContentAPI Schema
    subject: Annotated[list[CVItemWithCode], fields.nested_list(include_in_parent=True), Field(default_factory=list)]

    # Populated on fetch, never stored with the item
    user_has_access: bool = Field(alias="_access", default=False)
