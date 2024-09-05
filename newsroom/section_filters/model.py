from typing import Optional
from newsroom.core.resources.model import NewshubResourceModel


class SectionFilter(NewshubResourceModel):
    name: str
    description: Optional[str]
    sd_product_id: Optional[str] = None
    query: Optional[str] = None
    is_enabled: bool = True
    filter_type: Optional[str] = "wire"
    search_type: Optional[str] = "wire"
