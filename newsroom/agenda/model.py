from datetime import datetime

from superdesk.core.resources import ResourceModel, validators
from typing_extensions import Annotated


class FeaturedResourceModel(ResourceModel):
    _id: Annotated[
        str,
        validators.validate_iunique_value_async(resource_name="agenda_featured", field_name="_id"),
    ]
    tz: str | None = None
    items: list[str] | None = None
    display_from: datetime | None = None
    display_to: datetime | None = None
