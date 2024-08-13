from typing import Optional
from bson import ObjectId

from superdesk.flask import request, session, abort, g

from newsroom.companies.companies_async import CompanyService, CompanyResource

from .model import UserResourceModel
from .service import UsersService


def get_user_id():
    """Get user for current user.

    Make sure it's an ObjectId.
    """
    if request and session.get("user"):
        return ObjectId(session.get("user"))
    return None


async def get_user_async(required=False) -> Optional[UserResourceModel]:
    """
    Get current user.

    If user is required but not set it returns None

    :param required: Is user required.
    """
    user_id = get_user_id()
    user = None

    if user_id:
        user = await UsersService().find_by_id(user_id)

    if not user and required:
        return None

    return user


async def get_user_or_abort() -> Optional[UserResourceModel]:
    """Use when there must be a user authenticated."""

    user = await get_user_async(True)

    if not user:
        abort(401)

    return user


async def get_company_from_user(user: UserResourceModel) -> Optional[CompanyResource]:
    """
    Retrieve the company associated with the given user, if it exists.
    """
    if not user.company:
        return None

    return await CompanyService().find_by_id(user.company)


async def get_company_from_user_or_session(
    user: Optional[UserResourceModel] = None, is_user_required: bool = False
) -> Optional[CompanyResource]:
    """
    Retrieve the company associated with the user or from the session if available.

    Args:
        user (Optional[UserResourceModel]): The user resource model. Defaults to None.
        is_user_required (bool): Flag to indicate if a user is required. Defaults to False.

    Returns:
        Optional[CompanyResource]: The company resource associated with the user or session, or None if not found.
    """

    if user is None:
        user = await get_user_async(required=is_user_required)

    if user and user.company:
        return await get_company_from_user(user)

    # if there is no user this might be company session (in news api)
    if hasattr(g, "company_id"):
        return await CompanyService().find_by_id(g.company_id)

    return None
