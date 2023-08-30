from bson import ObjectId
from typing import Dict, List, TypedDict, Any
from datetime import datetime
from enum import Enum


class Product(TypedDict, total=False):
    _id: ObjectId
    name: str
    product_type: str
    navigations: List[str]


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


class UserData(TypedDict, total=False):
    _id: ObjectId
    email: str
    first_name: str
    last_name: str
    user_type: str
    company: ObjectId
    is_enabled: bool
    is_validated: bool
    sections: Dict[str, bool]
    products: List[ProductRef]
    dashboards: List[UserDashboardEntry]
    notification_schedule: NotificationSchedule


class User(UserData):
    pass


class UserAuth(TypedDict):
    _id: str
    email: str
    password: str
    is_enabled: bool
    is_approved: bool


class AuthProviderType(Enum):
    PASSWORD = "password"
    GOOGLE_OAUTH = "google_oauth"
    SAML = "saml"


class AuthProviderFeatures(TypedDict, total=False):
    verify_email: bool


class AuthProvider(TypedDict):
    _id: str
    name: str
    auth_type: AuthProviderType
    features: AuthProviderFeatures


class Company(TypedDict, total=False):
    _id: ObjectId
    name: str
    products: List[ProductRef]
    sections: Dict[str, bool]
    restrict_coverage_info: bool
    auth_provider: str


class TopicSubscriber(TypedDict):
    user_id: ObjectId
    notification_type: str


class Topic(TypedDict):
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
