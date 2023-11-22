from bson import ObjectId
from typing import Dict, List, TypedDict, Any, Union, NoReturn
from datetime import datetime
from enum import Enum
from flask_babel import LazyString


def assert_never(value: NoReturn) -> NoReturn:
    assert False, f"Unhandled value {value}"


NameString = Union[str, LazyString]


class Product(TypedDict, total=False):
    _id: ObjectId
    name: str
    description: str
    original_creator: ObjectId
    version_creator: ObjectId
    sd_product_id: str
    query: str
    planning_item_query: str
    is_enabled: bool
    product_type: str
    navigations: List[ObjectId]
    companies: List[ObjectId]


class ProductRef(TypedDict):
    _id: ObjectId
    seats: int
    section: str


class NotificationSchedule(TypedDict, total=False):
    timezone: str
    times: List[str]
    last_run_time: datetime


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
    user_type: str


class UserData(UserRequired, total=False):
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
    sections: Dict[str, bool]
    dashboards: List[UserDashboardEntry]
    notification_schedule: NotificationSchedule


class User(UserData):
    _id: ObjectId


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
    products: List[ProductRef]
    sections: Dict[str, bool]
    restrict_coverage_info: bool
    auth_provider: str


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
    topic_type: str
    navigation: List[str]
    original_creator: ObjectId
    version_creator: ObjectId
    folder: ObjectId
    advanced: Dict[str, Any]
    subscribers: List[TopicSubscriber]
