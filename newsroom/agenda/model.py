from datetime import datetime
from typing import List, Optional

from newsroom.core.resources.model import NewshubResourceModel


class FeaturedResourceModel(NewshubResourceModel):
    _id: str
    tz: Optional[str] = None
    items: Optional[List[str]] = None
    display_from: Optional[datetime] = None
    display_to: Optional[datetime] = None
