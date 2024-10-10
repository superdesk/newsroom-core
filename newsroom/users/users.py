# TODO-ASYNC: Remove this entire module

import newsroom
import superdesk

from superdesk.flask import request

from newsroom.types import PRODUCT_TYPES, UserRole
from newsroom.auth.eve_auth import SessionAuth


class UserAuthentication(SessionAuth):
    def authorized(self, allowed_roles, resource, method):
        from newsroom.auth.utils import get_user_or_none_from_request

        if super().authorized(allowed_roles, resource, method):
            return True

        user = get_user_or_none_from_request(None)
        if not user:
            return False

        if not request.view_args or not request.view_args.get("_id"):
            # not a request for a specific user, stop
            return False

        if request.view_args["_id"] == str(user.id):
            # current user editing current user
            return True

        if not user.company or not user.is_company_admin():
            # current user not a company admin
            return False

        request_user = superdesk.get_resource_service("users").find_one(req=None, _id=request.view_args["_id"])
        if request_user.get("company") and request_user["company"] == user.company:
            # if current user is a company admin for request user
            return True

        return False


class UsersResource(newsroom.Resource):
    """
    Users schema
    """

    # Use a private style URL, otherwise ``POST /users/<_id>`` doesn't work from behave tests
    url = "_users"

    authentication = UserAuthentication()

    schema = {
        "password": {"type": "string", "minlength": 8},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "email": {"unique": True, "type": "string", "required": True},
        "phone": {"type": "string", "nullable": True},
        "mobile": {"type": "string", "nullable": True},
        "role": {"type": "string", "nullable": True},
        "signup_details": {"type": "dict"},
        "country": {"type": "string"},
        "company": newsroom.Resource.rel("companies", embeddable=True, required=False),
        "user_type": {
            "type": "string",
            "allowed": [role.value for role in UserRole],
            "default": "public",
        },
        # user must have his auth method validated in order to login
        "is_validated": {"type": "boolean", "default": False},
        # user must be enabled in order to login
        "is_enabled": {"type": "boolean", "default": True},
        # flag if user was approved, applies to users who registers themselves,
        # they must be approved within predefined time otherwise they won't be
        # able to login
        "is_approved": {"type": "boolean", "default": False},
        "expiry_alert": {"type": "boolean", "default": False},
        "token": {
            "type": "string",
        },
        "token_expiry_date": {
            "type": "datetime",
        },
        "receive_email": {"type": "boolean", "default": True},
        "receive_app_notifications": {"type": "boolean", "default": True},
        "locale": {
            "type": "string",
        },
        "manage_company_topics": {"type": "boolean", "default": False},
        "last_active": {"type": "datetime", "required": False, "nullable": True},
        "original_creator": newsroom.Resource.rel("users"),
        "version_creator": newsroom.Resource.rel("users"),
        "products": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "_id": newsroom.Resource.rel("products", required=True),
                    "section": {"type": "string", "required": True, "allowed": PRODUCT_TYPES},
                },
            },
        },
        "sections": {
            "type": "dict",
            "nullable": True,
        },
        "dashboards": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "topic_ids": {
                        "type": "list",
                        "schema": newsroom.Resource.rel("topics"),
                    },
                },
            },
        },
        "notification_schedule": {
            "type": "dict",
            "nullable": True,
            "schema": {
                "timezone": {
                    "type": "string",
                    "required": True,
                },
                "times": {
                    "type": "list",
                    "required": True,
                    "schema": {"type": "string"},
                },
                "last_run_time": {
                    "type": "datetime",
                },
                "pause_from": {
                    "type": "string",
                },
                "pause_to": {
                    "type": "string",
                },
            },
        },
    }

    item_methods = ["GET", "PATCH", "PUT", "DELETE"]
    resource_methods = ["GET", "POST"]
    datasource = {
        "source": "users",
        "projection": {"password": 0, "token": 0},
        "default_sort": [("first_name", 1)],
    }
    mongo_indexes = {
        "email": (
            [("email", 1)],
            {"unique": True, "collation": {"locale": "en", "strength": 2}},
        )
    }


class AuthUserResource(newsroom.Resource):
    internal_resource = True

    schema = {
        "email": UsersResource.schema["email"],
        "password": UsersResource.schema["password"],
        "token": UsersResource.schema["token"],
        "token_expiry_date": UsersResource.schema["token_expiry_date"],
        "is_enabled": UsersResource.schema["is_enabled"],
    }

    datasource = {
        "source": "users",
    }


USER_PROFILE_UPDATES = {
    "locale",
    "first_name",
    "last_name",
    "phone",
    "mobile",
    "country",
    "receive_email",
    "receive_app_notifications",
    "role",
    "dashboards",
    "notification_schedule",
    "expiry_alert",
    "_updated",
    "password",
    "version_creator",
}


COMPANY_ADMIN_ALLOWED_UPDATES = USER_PROFILE_UPDATES.union(
    {
        "email",
        "is_approved",
        "is_enabled",
        "expiry_alert",
        "manage_company_topics",
        # populated by system
        "_created",
        "_updated",
        "token",
        "token_expiry_date",
    }
)

COMPANY_ADMIN_ALLOWED_PRODUCT_UPDATES = {
    "sections",
    "products",
}


class UsersService(newsroom.Service):
    """
    A service that knows how to perform CRUD operations on the `users`
    collection.

    Serves mainly as a proxy to the data layer.
    """


class AuthUserService(newsroom.Service):
    pass


users_service = UsersService()
