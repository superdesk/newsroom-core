from enum import Enum
from bson import ObjectId
from typing import Annotated

from superdesk.core.resources import validators
from superdesk.core.resources.fields import Field
from newsroom.core.resources.model import NewshubResourceModel
from newsroom.core.resources.validators import validate_multi_field_iunique_value_async

PRODUCT_TYPES = ["wire", "agenda", "news_api"]


class ProductType(str, Enum):
    WIRE = "wire"
    AGENDA = "agenda"
    NEWS_API = "news_api"


class ProductResourceModel(NewshubResourceModel):
    name: Annotated[
        str,
        validate_multi_field_iunique_value_async("products", ["name", "product_type"]),
    ]
    description: str | None = None
    sd_product_id: str | None = None
    query: str | None = None
    planning_item_query: str | None = None
    is_enabled: bool = True
    product_type: ProductType = ProductType.WIRE
    navigations: list[Annotated[ObjectId, validators.validate_data_relation_async("navigations")]] = Field(
        default_factory=list
    )

    # obsolete
    # TODO: check with the team why it is obsolete
    companies: list[Annotated[ObjectId, validators.validate_data_relation_async("companies")]] = Field(
        default_factory=list
    )
