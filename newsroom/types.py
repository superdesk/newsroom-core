from bson import ObjectId
from typing import Dict, List, TypedDict


class Product(TypedDict, total=False):
    _id: ObjectId
    name: str
    product_type: str
    navigations: List[str]


class ProductRef(TypedDict):
    _id: ObjectId
    seats: int
    section: str


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


class User(UserData):
    pass


class Company(TypedDict, total=False):
    _id: ObjectId
    name: str
    products: List[ProductRef]
    sections: Dict[str, bool]
    restrict_coverage_info: bool
