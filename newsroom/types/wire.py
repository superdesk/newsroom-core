from typing import Annotated

from pydantic import Field

from superdesk.core.resources import fields
from content_api.items.model import ContentAPIItem, CVItemWithCode


class WireItem(ContentAPIItem):
    products: Annotated[list[CVItemWithCode], Field(default_factory=list)]

    bookmarks: Annotated[list[fields.ObjectId], fields.keyword_mapping(), Field(default_factory=list)]
    downloads: Annotated[list[fields.Keyword], fields.keyword_mapping(), Field(default_factory=list)]
    shares: Annotated[list[fields.Keyword], fields.keyword_mapping(), Field(default_factory=list)]
    prints: Annotated[list[fields.Keyword], fields.keyword_mapping(), Field(default_factory=list)]
    copies: Annotated[list[fields.Keyword], fields.keyword_mapping(), Field(default_factory=list)]

    # Overrides from ContentAPI Schema
    subject: Annotated[list[CVItemWithCode], fields.nested_list(include_in_parent=True), Field(default_factory=list)]

    # Populated on fetch, never stored with the item
    user_has_access: bool = Field(alias="_access", default=False)
