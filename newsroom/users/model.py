from datetime import datetime

from pydantic import Field
from typing import Annotated, Any, Dict, List, Optional

from newsroom.user_roles import UserRole
from newsroom.companies.companies_async import CompanyProduct
from newsroom.core.resources.model import NewshubResourceModel

from superdesk.core.resources.fields import ObjectId as ObjectIdField
from superdesk.core.resources import dataclass
from superdesk.core.resources.validators import (
    validate_minlength,
    validate_email,
    validate_iunique_value_async,
    validate_data_relation_async,
)


@dataclass
class Dashboard:
    name: str
    type: str
    topic_ids: Annotated[list[ObjectIdField], validate_data_relation_async("topics")]


@dataclass
class NotificationSchedule:
    timezone: str
    times: List[str]
    last_run_time: datetime
    pause_from: str
    pause_to: str


class UserResourceModel(NewshubResourceModel):
    password: Annotated[str, validate_minlength(8)]
    first_name: str
    last_name: str
    email: Annotated[str, validate_email(), validate_iunique_value_async("users", "email")]
    phone: Optional[str] = None
    mobile: Optional[str] = None
    role: Optional[str] = None
    signup_details: Optional[Dict[str, Any]] = None
    country: str
    company: Annotated[Optional[ObjectIdField], validate_data_relation_async("companies")] = None
    user_type: UserRole = Field(default=UserRole.PUBLIC)

    is_validated: bool = False
    is_enabled: bool = True

    # Flag is_approved, applies to users who registers themselves.
    # They must be approved within predefined time otherwise they won't be able to login
    is_approved: bool = False
    expiry_alert: bool = False

    token: str
    token_expiry_date: datetime

    receive_email: bool = True
    receive_app_notifications: bool = True

    locale: str
    manage_company_topics: bool = False
    last_active: Optional[datetime] = None

    products: Optional[List[CompanyProduct]] = None
    sections: Optional[dict[str, bool]] = None
    dashboards: Optional[List[Dashboard]] = None
    notification_schedule: Optional[NotificationSchedule] = None
