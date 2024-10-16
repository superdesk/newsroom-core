from typing import Annotated, Optional

from newsroom.core.resources.model import NewshubResourceModel
from newsroom.core.resources.validators import validate_multi_field_iunique_value_async


class NavigationModel(NewshubResourceModel):
    name: Annotated[str, validate_multi_field_iunique_value_async("navigations", ["name", "product_type"])]
    description: str = ""
    is_enabled: bool = True
    order: Optional[int] = None
    product_type: str = "wire"
    tile_images: Optional[list[str]] = None
