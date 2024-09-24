from bson import ObjectId
from typing import Dict, List, Literal, Optional, TypedDict, Any, Union, NoReturn
from datetime import datetime
from enum import Enum
from quart_babel.speaklater import LazyString


def assert_never(value: NoReturn) -> NoReturn:
    assert False, f"Unhandled value {value}"


NameString = Union[str, LazyString]
NavigationIds = List[Union[str, ObjectId]]
Section = Literal["wire", "agenda", "monitoring", "news_api", "media_releases", "factcheck", "am_news", "aapX"]
SectionAllowedMap = Dict[Section, bool]
Permissions = Literal["coverage_info"]


class Group(TypedDict):
    field: str
    label: str
    nested: dict
    permissions: List[Permissions]


class Country(TypedDict):
    value: str
    text: str


class Entity(TypedDict):
    _id: ObjectId


class Product(Entity, total=False):
    name: str
    description: str
    original_creator: ObjectId
    version_creator: ObjectId
    sd_product_id: str
    query: str
    planning_item_query: str
    is_enabled: bool
    product_type: Section
    navigations: NavigationIds
    companies: List[ObjectId]


class ProductRef(TypedDict):
    _id: ObjectId
    seats: int
    section: Section


class NotificationSchedule(TypedDict, total=False):
    timezone: str
    times: List[str]
    last_run_time: datetime
    pause_from: str
    pause_to: str


class NotificationQueueTopic(TypedDict, total=False):
    items: List[str]
    topic_id: ObjectId
    last_item_arrived: datetime
    section: str


class NotificationQueue(TypedDict):
    user: ObjectId
    topics: List[NotificationQueueTopic]


class UserDashboardEntry(TypedDict):
    name: str
    type: str
    topic_ids: List[ObjectId]


class UserRequired(TypedDict):
    email: str
    user_type: Literal["administrator", "internal", "public", "company_admin", "account_management"]


class UserData(UserRequired, total=False):
    _id: ObjectId
    first_name: str
    last_name: str
    phone: str
    mobile: str
    role: str
    signup_details: Dict[str, Any]
    country: str
    company: ObjectId
    is_validated: bool
    is_enabled: bool
    is_approved: bool

    expiry_alert: bool
    receive_email: bool
    receive_app_notifications: bool
    locale: str
    manage_company_topics: bool
    last_active: datetime

    original_creator: ObjectId
    version_creator: ObjectId

    products: List[ProductRef]
    sections: SectionAllowedMap
    dashboards: List[UserDashboardEntry]
    notification_schedule: NotificationSchedule


class User(UserData):
    pass


class PublicUserData(TypedDict):
    _id: str
    company: str
    first_name: str
    last_name: str
    email: str
    products: List[ProductRef]
    sections: SectionAllowedMap
    notification_schedule: Optional[NotificationSchedule]


class UserAuth(TypedDict):
    _id: str
    email: str
    token: str
    password: str
    is_enabled: bool
    is_approved: bool


class AuthProviderType(Enum):
    PASSWORD = "password"
    GOOGLE_OAUTH = "google_oauth"
    SAML = "saml"
    FIREBASE = "firebase"


class AuthProviderConfig(TypedDict):
    _id: str
    name: NameString
    auth_type: AuthProviderType


class CompanyRequired(TypedDict):
    _id: ObjectId
    name: str


class Company(CompanyRequired, total=False):
    # Accounting/Auditing
    original_creator: ObjectId
    version_creator: ObjectId

    # Company details
    url: str
    contact_name: str
    contact_email: str
    phone: str
    country: str
    company_type: str
    account_manager: str
    monitoring_administrator: ObjectId
    company_size: str
    referred_by: str

    # Authentication
    auth_provider: str
    auth_domains: List[str]
    is_enabled: bool
    is_approved: bool
    expiry_date: datetime

    # Authorization
    products: List[ProductRef]
    sections: SectionAllowedMap
    restrict_coverage_info: bool
    sd_subscriber_id: str
    archive_access: bool
    events_only: bool
    allowed_ip_list: List[str]  # Used by the NewsAPI


class CompanyTypeRequired(TypedDict):
    id: str
    name: str


class CompanyType(CompanyTypeRequired, total=False):
    wire_must: Dict[str, Any]
    must_not: Dict[str, Any]


class TopicSubscriber(TypedDict):
    user_id: ObjectId
    notification_type: str


class Topic(TypedDict, total=False):
    _id: ObjectId
    label: str
    query: str
    filter: Dict[str, Any]
    created: Dict[str, Any]
    user: ObjectId
    company: ObjectId
    is_global: bool
    timezone_offset: int
    topic_type: Section
    navigation: NavigationIds
    original_creator: ObjectId
    version_creator: ObjectId
    folder: ObjectId
    advanced: Dict[str, Any]
    subscribers: List[TopicSubscriber]


class SectionFilter(TypedDict, total=False):
    name: str
    description: str
    sd_product_id: str
    query: str
    is_enabled: bool
    filter_type: Section
    search_type: Section
    original_creator: ObjectId
    version_creator: ObjectId


Article = Dict[str, Any]


class Navigation(Entity):
    name: str
