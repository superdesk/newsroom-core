from typing import TypedDict


class UserData(TypedDict, total=False):
    _id: str
    email: str
    first_name: str
    last_name: str
    user_type: str
    company: str
    is_enabled: bool
    is_validated: bool
