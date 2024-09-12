from typing import Optional
from newsroom.core.resources.model import NewshubResourceModel


class Navigation(NewshubResourceModel):
    name: str
    description: str = ""
    is_enabled: bool = True
    order: Optional[int] = None
    product_type: str = "wire"
    tile_images: Optional[list[str]] = None
