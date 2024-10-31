from datetime import datetime, date

import pytz
from pydantic import Field
from typing import Annotated, List, Optional
from dataclasses import asdict
from quart_babel import lazy_gettext

from superdesk.core import get_app_config
from superdesk.core.resources.fields import ObjectId as ObjectIdField
from superdesk.core.resources import dataclass
from superdesk.core.resources.validators import (
    validate_minlength,
    validate_email,
    validate_iunique_value_async,
    validate_data_relation_async,
)

from newsroom.core.resources.model import NewshubResourceModel

from .company import CompanyProduct, CompanyResource
from .user_roles import UserRole


@dataclass
class DashboardModel:
    name: str
    type: str
    topic_ids: Annotated[list[ObjectIdField], validate_data_relation_async("topics")]

    def to_dict(self):
        return asdict(self)


@dataclass
class NotificationScheduleModel:
    timezone: str
    times: List[str]
    last_run_time: Optional[datetime] = None
    pause_from: Optional[str] = None
    pause_to: Optional[str] = None


class UserResourceModel(NewshubResourceModel):
    first_name: str
    last_name: str
    email: Annotated[
        str,
        validate_email(),
        validate_iunique_value_async("users", "email", lazy_gettext("Email address is already in use")),
    ]
    phone: Optional[str] = None
    mobile: Optional[str] = None
    role: Optional[str] = None
    company: Annotated[Optional[ObjectIdField], validate_data_relation_async("companies")] = None
    user_type: UserRole = Field(default=UserRole.PUBLIC)

    country: Optional[str] = None

    is_validated: bool = False
    is_enabled: bool = True

    # Flag is_approved, applies to users who registers themselves.
    # They must be approved within predefined time otherwise they won't be able to login
    is_approved: bool = False
    expiry_alert: bool = False

    receive_email: bool = True
    receive_app_notifications: bool = True

    locale: Optional[str] = None
    manage_company_topics: bool = False
    last_active: Optional[datetime] = None

    products: Optional[List[CompanyProduct]] = None
    sections: Optional[dict[str, bool]] = None
    dashboards: Optional[List[DashboardModel]] = None
    notification_schedule: Optional[NotificationScheduleModel] = None

    def is_admin(self) -> bool:
        return self.user_type == UserRole.ADMINISTRATOR

    def is_internal(self) -> bool:
        return self.user_type == UserRole.INTERNAL

    def is_admin_or_internal(self) -> bool:
        return self.user_type in [
            UserRole.ADMINISTRATOR,
            UserRole.ACCOUNT_MANAGEMENT,
            UserRole.INTERNAL,
        ]

    def is_account_manager(self) -> bool:
        return self.user_type == UserRole.ACCOUNT_MANAGEMENT

    def is_company_admin(self) -> bool:
        return self.user_type == UserRole.COMPANY_ADMIN

    async def get_company(self) -> CompanyResource | None:
        from newsroom.companies.companies_async import CompanyService

        if self.company:
            return await CompanyService().find_by_id(self.company)
        return None

    def has_paused_notifications(self) -> bool:
        if not self.notification_schedule:
            return False

        timezone = pytz.timezone(self.notification_schedule.timezone or get_app_config("DEFAULT_TIMEZONE") or "UTC")
        if self.notification_schedule.pause_from is not None and self.notification_schedule.pause_to is not None:
            now = datetime.now(timezone).date()
            pause_from_date = date.fromisoformat(self.notification_schedule.pause_from)
            pause_to_date = date.fromisoformat(self.notification_schedule.pause_to)

            return pause_from_date <= now <= pause_to_date

        return False


class UserAuthResourceModel(UserResourceModel):
    password: Optional[Annotated[str, validate_minlength(8)]] = None
    token: Optional[str] = None
    token_expiry_date: Optional[datetime] = None
