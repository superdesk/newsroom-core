from bson import ObjectId
from typing import Dict, List, Optional, TypedDict


class UserData(TypedDict, total=False):
    _id: str
    email: str
    first_name: str
    last_name: str
    user_type: str
    company: str
    is_enabled: bool
    is_validated: bool
    sections: Dict[str, bool]


class User(UserData):
    pass


class Product(TypedDict, total=False):
    _id: str
    name: str
    product_type: str
    navigations: List[str]


class ProductRef(TypedDict):
    _id: str
    seats: Optional[int]
    section: str


class Company(TypedDict, total=False):
    _id: ObjectId
    name: str
    products: List[ProductRef]
    sections: Dict[str, bool]
