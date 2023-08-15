from bson import ObjectId
from typing import Dict, List, TypedDict
from datetime import datetime


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


class Company(TypedDict, total=False):
    _id: ObjectId
    name: str
    products: List[ProductRef]
    sections: Dict[str, bool]
    restrict_coverage_info: bool
