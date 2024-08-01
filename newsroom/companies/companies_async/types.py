from typing import Annotated, Optional
from datetime import datetime
from pydantic import Field

from superdesk.core.resources import dataclass
from superdesk.core.resources.validators import validate_data_relation_async, validate_iunique_value_async
from superdesk.core.resources.fields import ObjectId

from newsroom.core.resources import NewshubResourceModel, validate_ip_address, validate_auth_provider
from newsroom.products.types import ProductType


@dataclass
class CompanyProduct:
    _id: Annotated[ObjectId, validate_data_relation_async("products")]
    section: ProductType
    seats: int = 0


class CompanyResource(NewshubResourceModel):
    name: Annotated[str, validate_iunique_value_async("companies", "name")]
    url: Optional[str] = None
    sd_subscriber_id: Optional[str] = None
    is_enabled: bool = True
    is_approved: bool = True
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    expiry_date: Optional[datetime] = None
    sections: Optional[dict[str, bool]] = None
    archive_access: bool = False
    events_only: bool = False
    restrict_coverage_info: bool = False
    company_type: Optional[str] = None
    account_manager: Optional[str] = None
    monitoring_administrator: Optional[ObjectId] = None
    allowed_ip_list: Annotated[
        Optional[list[str]],
        validate_ip_address(),
    ] = None

    products: Optional[list[CompanyProduct]] = None

    auth_domain: Optional[str] = None  # Deprecated
    auth_domains: Optional[list[str]] = None
    auth_provider: Annotated[Optional[str], validate_auth_provider()] = None
    company_size: Optional[str] = None
    referred_by: Optional[str] = None
