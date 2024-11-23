from datetime import datetime
from enum import Enum, unique

from superdesk.core.resources import dataclass
from superdesk.core.resources.fields import ObjectId
from newsroom.core.resources import NewshubResourceModel


@unique
class MonitoringScheduleInterval(str, Enum):
    IMMEDIATE = "immediate"
    ONE_HOUR = "one_hour"
    TWO_HOUR = "two_hour"
    FOUR_HOUR = "four_hour"
    WEEKLY = "weekly"
    DAILY = "daily"


@dataclass
class MonitoringSchedule:
    interval: MonitoringScheduleInterval
    time: str | None = None
    day: str | None = None


class MonitoringProfileResourceModel(NewshubResourceModel):
    name: str
    subject: str | None = None
    description: str | None = None
    company: ObjectId | None = None
    query: str | None = None
    alert_type: str | None = None
    is_enabled: bool = True
    users: list[ObjectId] | None = None
    schedule: MonitoringSchedule | None = None
    keywords: list[str] | None = None
    last_run_time: datetime | None = None
    format_type: str | None = None
    always_send: bool = False
    headline_subject: bool = False
