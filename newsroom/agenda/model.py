from datetime import datetime

from newsroom.core.resources.model import NewshubResourceModel


class FeaturedResourceModel(NewshubResourceModel):
    tz: str | None = None
    items: list[str] | None = None
    display_from: datetime | None = None
    display_to: datetime | None = None
