from pydantic import Field
from datetime import datetime

from superdesk.core.resources import ResourceModel
from typing_extensions import Annotated


class FeaturedResourceModel(ResourceModel):
    id: Annotated[str, Field(alias="_id")]
    tz: str | None = None
    items: list[str] | None = None
    display_from: datetime | None = None
    display_to: datetime | None = None
