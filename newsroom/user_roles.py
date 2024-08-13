from enum import Enum, unique


@unique
class UserRole(str, Enum):
    ADMINISTRATOR = "administrator"
    INTERNAL = "internal"
    PUBLIC = "public"
    COMPANY_ADMIN = "company_admin"
    ACCOUNT_MANAGEMENT = "account_management"
