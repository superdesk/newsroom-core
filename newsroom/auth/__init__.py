from typing import Optional
import re

from bson import ObjectId
from eve.auth import BasicAuth

import superdesk
from superdesk.flask import session, abort, request, g
from newsroom.types import Company, User, UserAuth


class SessionAuth(BasicAuth):
    def authorized(self, allowed_roles, resource, method):
        if not get_user_id():
            return False
        if not resource:
            return True  # list of apis is open
        user_role = session.get("user_type") if request else None
        return user_role in allowed_roles


def get_user(required=False) -> Optional[User]:
    """Get current user.

    If user is required but not set abort.

    :param required: Is user required.
    """
    user_id = get_user_id()
    user = None
    if user_id:
        user = superdesk.get_resource_service("users").find_one(req=None, _id=user_id)
    if not user and required:
        abort(401)
    return user


def get_user_required() -> User:
    """Use when there must be a user authenticated."""
    user = get_user(True)
    assert user is not None
    return user


def get_company(user=None, required=False) -> Optional[Company]:
    if user is None:
        user = get_user(required=required)
    if user and user.get("company"):
        return get_company_from_user(user)
    if hasattr(g, "company_id"):  # if there is no user this might be company session (in news api)
        return superdesk.get_resource_service("companies").find_one(req=None, _id=g.company_id)
    return None


def get_company_from_user(user: User) -> Optional[Company]:
    if user.get("company"):
        return superdesk.get_resource_service("companies").find_one(req=None, _id=user["company"])

    return None


def get_user_id():
    """Get user for current user.

    Make sure it's an ObjectId.
    """
    if request and session.get("user"):
        return ObjectId(session.get("user"))
    return None


def get_auth_user_by_email(email) -> Optional[UserAuth]:
    """Returns the user from auth by the email case insensitive"""
    return _get_user_by_email(email, "auth_user")


def get_user_by_email(email) -> Optional[User]:
    """Returns the user from users by the email case insensitive"""
    return _get_user_by_email(email, "users")


def _get_user_by_email(email, repo):
    lookup = {"email": {"$regex": re.compile("^{}$".format(re.escape(email)), re.IGNORECASE)}}
    users = list(superdesk.get_resource_service(repo).get(req=None, lookup=lookup))
    return users[0] if users else None
