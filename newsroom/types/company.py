from typing import Annotated, Optional
from datetime import datetime
from enum import Enum, unique

from superdesk.core.resources import Dataclass
from superdesk.core.resources.validators import validate_data_relation_async, validate_iunique_value_async
from superdesk.core.resources.fields import ObjectId, Field

from newsroom.core.resources import NewshubResourceModel, validate_ip_address, validate_auth_provider

from .common import SectionEnum


class CompanyProduct(Dataclass):
    _id: Annotated[ObjectId, validate_data_relation_async("products")]
    section: SectionEnum
    seats: int = 0


@unique
class EmbedPermissionUserAction(str, Enum):
    DISPLAY = "display"
    DOWNLOAD = "download"


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
    sections: dict[str, bool] = Field(default_factory=dict)
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

    products: list[CompanyProduct] = Field(default_factory=list)

    auth_domain: Optional[str] = None  # Deprecated
    auth_domains: Annotated[Optional[list[str]], validate_iunique_value_async("companies", "auth_domains")] = None
    auth_provider: Annotated[Optional[str], validate_auth_provider()] = None
    company_size: Optional[str] = None
    referred_by: Optional[str] = None
    internal: bool = False

    embed_permissions: dict[str, list[EmbedPermissionUserAction]] = Field(default_factory=dict)

    def is_permissioned_for_embed(self, content_type: str, user_action: str, default: bool | None = None) -> bool:
        try:
            return user_action in self.embed_permissions[content_type]
        except KeyError:
            # By default, Companies have access to all embedded content unless configured otherwise
            return default if default is not None else True
