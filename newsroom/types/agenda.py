from typing import Annotated, Any
from datetime import datetime, timezone
from enum import Enum, unique

from pydantic import Field, field_validator, model_validator

from superdesk.core.resources import ResourceModel, fields, dataclass, ModelWithVersions
from superdesk.utc import utcnow
from content_api.items.model import Place, CVItemWithCode, CVItem, PubStatusType


def convert_value_to_bool(value: bool | None) -> bool:
    """This allows to support None values for fields that require a boolean"""

    return bool(value)


def convert_none_to_utcnow(value: datetime | None) -> datetime:
    """This allows to support None values for fields that require a datetime"""

    return datetime.now(timezone.utc) if value is None else value


def convert_none_to_list(value: list | None) -> list:
    """This allows to support None values for fields that require a list"""

    return [] if value is None else value


@unique
class AgendaItemType(str, Enum):
    EVENT = "event"
    PLANNING = "planning"


@unique
class AgendaWorkflowState(str, Enum):
    SCHEDULED = "scheduled"
    KILLED = "killed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    POSTPONED = "postponed"


@dataclass
class AgendaCVItem:
    code: fields.Keyword
    name: fields.Keyword
    qcode: fields.Keyword | None = None
    scheme: fields.Keyword | None = None
    parent: fields.Keyword | None = None
    translations: dict[str, dict[str, str | None]] | None = None


@dataclass
class EventRecurringRule:
    frequency: str | None = None
    interval: int | None = None
    endRepeatMode: str | None = None
    until: datetime | None = None
    count: int | None = None
    _created_externally: bool | None = None


@dataclass
class AgendaDates:
    start: datetime
    end: datetime
    tz: str | None = None
    all_day: bool = False
    no_end_time: bool = False
    recurring_rule: EventRecurringRule | None = None

    # Field validators
    _parse_no_end_time = field_validator("all_day", "no_end_time", mode="before")(convert_value_to_bool)


@dataclass
class AgendaDisplayDates:
    date: datetime


@dataclass
class AgendaCoverageDelivery:
    delivery_id: fields.Keyword | None = None
    delivery_href: fields.Keyword | None = None
    sequence_no: Annotated[int, fields.keyword_mapping()] = 0
    publish_time: datetime | None = None
    delivery_state: fields.Keyword | None = None


@dataclass
class AgendaCoverage:
    planning_id: fields.Keyword
    coverage_id: fields.Keyword
    scheduled: datetime
    coverage_type: fields.Keyword
    workflow_status: fields.Keyword
    coverage_status: fields.Keyword
    coverage_provider: fields.Keyword | None = None
    slugline: fields.HTML | None = None

    delivery_id: fields.Keyword | None = None
    delivery_href: fields.Keyword | None = None
    publish_time: datetime | None = None

    time_to_be_confirmed: Annotated[bool, Field(alias="_time_to_be_confirmed")] = False
    deliveries: list[AgendaCoverageDelivery] = Field(default_factory=list)
    watches: Annotated[list[fields.ObjectId], fields.keyword_mapping()] = Field(default_factory=list)

    genre: list[CVItem] = Field(default_factory=list)

    assigned_desk_name: fields.Keyword | None = None
    assigned_desk_email: Annotated[str | None, fields.not_indexed()] = None
    assigned_user_name: fields.Keyword | None = None
    assigned_user_email: Annotated[str | None, fields.not_indexed()] = None

    # Field validators
    _parse_time_to_be_confirmed = field_validator("time_to_be_confirmed", mode="before")(convert_value_to_bool)
    _parse_list_fields = field_validator(
        "deliveries",
        "watches",
        "genre",
        mode="before",
    )(convert_none_to_list)


@dataclass
class EventLocation:
    name: fields.TextWithKeyword
    address: Annotated[dict | None, fields.dynamic_mapping()] = None
    location: fields.Geopoint | None = None
    qcode: fields.Keyword | None = None
    geo: str | None = None
    formatted_address: str | None = None
    details: list[str] | None = None


@dataclass
class PlanningItemAgenda:
    _id: fields.Keyword
    name: fields.Keyword


@dataclass
class AgendaPlanningItem:
    _id: fields.Keyword
    guid: fields.Keyword
    planning_date: datetime
    state: fields.Keyword
    pubstatus: Annotated[PubStatusType | None, fields.keyword_mapping()] = None
    time_to_be_confirmed: Annotated[bool, Field(alias="_time_to_be_confirmed")] = False
    firstcreated: datetime = Field(default_factory=utcnow)
    versioncreated: datetime = Field(default_factory=utcnow)
    language: fields.Keyword | None = None
    source: fields.Keyword | None = None
    name: fields.Keyword | None = None
    slugline: fields.Keyword | None = None
    description_text: str | None = None
    headline: str | None = None
    abstract: str | None = None
    subject: Annotated[list[AgendaCVItem], fields.nested_list(include_in_parent=True)] = Field(default_factory=list)
    urgency: int | None = None
    service: list[AgendaCVItem] = Field(default_factory=list)
    coverages: Annotated[list[dict[str, Any]], fields.mapping_disabled("object")] = Field(default_factory=list)
    agendas: list[PlanningItemAgenda] = Field(default_factory=list)
    ednote: str | None = None
    internal_note: Annotated[str | None, fields.not_indexed()] = None
    place: list[Place] = Field(default_factory=list)
    state_reason: str | None = None
    products: list[CVItemWithCode] = Field(default_factory=list)
    event_ids: list[fields.Keyword] | None = None

    # Field validators
    _parse_time_to_be_confirmed = field_validator("time_to_be_confirmed", mode="before")(convert_value_to_bool)
    _parse_datetime_fields = field_validator("firstcreated", "versioncreated", mode="before")(convert_none_to_utcnow)
    _parse_list_fields = field_validator(
        "subject",
        "service",
        "coverages",
        "agendas",
        "place",
        "products",
        mode="before",
    )(convert_none_to_list)


@dataclass
class CalendarItem:
    qcode: fields.Keyword
    name: fields.Keyword
    schema: fields.Keyword | None = None
    is_active: bool = True
    translations: dict[str, Any] | None = None


class AgendaItem(ResourceModel, ModelWithVersions):
    id: Annotated[str, Field(alias="_id")]
    guid: fields.Keyword
    content_type: Annotated[fields.Keyword, Field(alias="type")] = "agenda"
    event_id: fields.Keyword | None = None
    item_type: Annotated[AgendaItemType, fields.keyword_mapping()]
    recurrence_id: fields.Keyword | None = None
    name: fields.HTML | None = None
    slugline: fields.HTML | None = None
    definition_short: fields.HTML | None = None
    definition_long: fields.HTML | None = None
    description_text: fields.HTML | None = None
    headline: fields.HTML | None = None
    firstcreated: datetime = Field(default_factory=utcnow)
    versioncreated: datetime = Field(default_factory=utcnow)
    version: int | None = None
    ednote: fields.HTML | None = None
    registration_details: str | None = None
    invitation_details: str | None = None
    language: fields.Keyword | None = None
    source: fields.Keyword | None = None

    urgency: Annotated[int | None, fields.keyword_mapping()] = None
    priority: Annotated[int | None, fields.keyword_mapping()] = None

    place: list[Place] = Field(default_factory=list)
    service: list[AgendaCVItem] = Field(default_factory=list)

    state_reason: str | None = None
    subject: Annotated[list[AgendaCVItem], fields.nested_list(include_in_parent=True), Field(default_factory=list)]
    dates: AgendaDates
    display_dates: list[AgendaDisplayDates] = Field(default_factory=list)

    coverages: Annotated[list[AgendaCoverage], fields.nested_list(include_in_parent=True), Field(default_factory=list)]

    files: Annotated[list[dict], fields.mapping_disabled("object"), Field(default_factory=list)]

    state: AgendaWorkflowState
    pubstatus: Annotated[PubStatusType | None, fields.keyword_mapping()] = None
    calendars: list[CalendarItem] = Field(default_factory=list)
    location: list[EventLocation] = Field(default_factory=list)
    event: dict | None = None

    bookmarks: Annotated[list[fields.ObjectId], fields.keyword_mapping(), Field(default_factory=list)]
    downloads: Annotated[list[fields.ObjectId], fields.keyword_mapping(), Field(default_factory=list)]
    shares: Annotated[list[fields.ObjectId], fields.keyword_mapping(), Field(default_factory=list)]
    prints: Annotated[list[fields.ObjectId], fields.keyword_mapping(), Field(default_factory=list)]
    copies: Annotated[list[fields.ObjectId], fields.keyword_mapping(), Field(default_factory=list)]
    watches: Annotated[list[fields.ObjectId], fields.keyword_mapping(), Field(default_factory=list)]

    products: Annotated[list[CVItemWithCode], Field(default_factory=list)]
    planning_items: Annotated[
        list[AgendaPlanningItem], fields.nested_list(include_in_parent=True), Field(default_factory=list)
    ]
    planning_ids: Annotated[list[fields.Keyword], Field(default_factory=list)]

    # Field/Model validators
    _parse_datetime_fields = field_validator("firstcreated", "versioncreated", mode="before")(convert_none_to_utcnow)
    _parse_list_fields = field_validator(
        "place",
        "service",
        "subject",
        "display_dates",
        "coverages",
        "files",
        "calendars",
        "location",
        "bookmarks",
        "downloads",
        "shares",
        "prints",
        "copies",
        "watches",
        "products",
        "planning_items",
        "planning_ids",
        mode="before",
    )(convert_none_to_list)

    @model_validator(mode="before")
    @classmethod
    def parse_dict(cls, values) -> dict[str, Any]:
        if not values.get("guid") and values.get("_id"):
            # Make sure there is a ``guid``
            values["guid"] = values["_id"]
        elif not values.get("_id") and values.get("guid"):
            # Make sure there is a ``_id``
            values["_id"] = values["guid"]

        return values
