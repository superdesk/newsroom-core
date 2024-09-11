from typing import Optional
from newsroom.core.resources.model import NewshubResourceModel


class Navigation(NewshubResourceModel):
    name: str
    description: Optional[str] = None
    is_enabled: bool = True
    order: Optional[int] = None
    product_type: Optional[str] = "wire"
    tile_images: Optional[list[str]] = None
