import bson
import werkzeug

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, TypedDict, Union
from quart_babel import gettext

import superdesk
from superdesk.core import get_current_app, get_app_config
from superdesk.flask import session, redirect, url_for

from newsroom.flask import flash
from newsroom.auth.providers import AuthProvider
from newsroom.exceptions import AuthorizationError
from newsroom.user_roles import UserRole
from superdesk.utc import utcnow
from newsroom.auth import get_user, get_company, get_user_by_email
from newsroom.types import Section, SectionAllowedMap, User, UserData, Company, AuthProviderType
from newsroom.utils import (
    get_random_string,
    is_valid_user,
    is_company_enabled,
    is_company_expired,
    is_account_enabled,
)
from newsroom.email import (
    send_validate_account_email,
    send_reset_password_email,
    send_new_account_email,
)


# how often we should check in db if session
# user is still valid
SESSION_AUTH_TTL = timedelta(minutes=15)


async def sign_user_by_email(
    email: str,
    auth_type: AuthProviderType,
    redirect_on_success: str = "wire.index",
    redirect_on_error: str = "auth.login",
    create_missing: bool = False,
    userdata: Optional[UserData] = None,
    validate_login_attempt: bool = False,
) -> werkzeug.Response:
    users = superdesk.get_resource_service("users")
    user: Union[User, UserData, None] = get_user_by_email(email)

    if user is None and create_missing and userdata is not None:
        user = userdata.copy()
        user["is_enabled"] = True
        user["is_approved"] = True
        users.create([user])
        assert "_id" in user

    async def redirect_with_error(error_str):
        session.pop("_flashes", None)
        await flash(error_str, "danger")
        return redirect(url_for(redirect_on_error, user_error=1))

    if user is None:
        return await redirect_with_error(gettext("User not found"))

    if validate_login_attempt:
        company = get_company(user)
        company_auth_provider = get_company_auth_provider(company)

        if company is None:
            return await redirect_with_error(gettext("No Company assigned"))
        elif not is_company_enabled(user, company):
            return await redirect_with_error(gettext("Company is disabled"))
        elif is_company_expired(user, company):
            return await redirect_with_error(gettext("Company has expired"))
        elif not await is_account_enabled(user):
            return await redirect_with_error(gettext("Account is disabled"))
        elif company_auth_provider.type != auth_type:
            return await redirect_with_error(
                gettext("Invalid login type, %(type)s not enabled for your user", type=auth_type.value)
            )

    users.system_update(
        user["_id"],
        {
            "is_validated": True,  # in case user was not validated before set it now
            "last_active": utcnow(),
        },
        user,
    )

    start_user_session(user)

    return redirect_to_next_url(redirect_on_success)


def start_user_session(user: User, permanent=False):
    session["user"] = str(user["_id"])  # str to avoid serialization issues
    session["name"] = "{} {}".format(user.get("first_name"), user.get("last_name"))
    session["user_type"] = user["user_type"]
    session["auth_ttl"] = utcnow().replace(tzinfo=None) + SESSION_AUTH_TTL
    session.permanent = permanent


def clear_user_session():
    session["user"] = None
    session["name"] = None
    session["user_type"] = None
    session["auth_ttl"] = None
    session["auth_user"] = None


def is_user_admin(user: User) -> bool:
    return user.get("user_type") == UserRole.ADMINISTRATOR.value


def is_current_user_admin() -> bool:
    return session.get("user_type") == UserRole.ADMINISTRATOR.value


def is_current_user_account_mgr() -> bool:
    return session.get("user_type") == UserRole.ACCOUNT_MANAGEMENT.value


def is_current_user_company_admin() -> bool:
    return session.get("user_type") == UserRole.COMPANY_ADMIN.value


def is_current_user(user_id):
    """
    Checks if the current session user is the same as given user id
    """
    return session["user"] == str(user_id)


async def send_token(user: User, token_type="validate", update_token=True):
    if user is not None and user.get("is_enabled", False):
        if token_type == "validate" and user.get("is_validated", False):
            return False

        token = user.get("token")
        if update_token:
            updates = get_token_data()
            superdesk.get_resource_service("users").system_update(bson.ObjectId(user["_id"]), updates, user)
            token = updates["token"]

        assert isinstance(token, str)

        if token_type == "validate":
            await send_validate_account_email(user, token)
        if token_type == "new_account":
            await send_new_account_email(user, token)
        elif token_type == "reset_password":
            await send_reset_password_email(user, token)
        return True
    return False


class TokenData(TypedDict):
    token: str
    token_expiry_date: datetime


def get_token_data() -> TokenData:
    return {
        "token": get_random_string(),
        "token_expiry_date": utcnow() + timedelta(days=get_app_config("VALIDATE_ACCOUNT_TOKEN_TIME_TO_LIVE")),
    }


def add_token_data(user):
    updates = get_token_data()
    user.update(updates)


async def is_valid_session():
    """Uses timezone-aware objects to avoid TypeError comparison"""
    # Get the current UTC time as a timezone-aware datetime
    now = datetime.now(timezone.utc)

    # Retrieve auth_ttl and ensure it is also timezone-aware
    auth_ttl = session.get("auth_ttl")
    if auth_ttl and isinstance(auth_ttl, datetime) and auth_ttl.tzinfo is None:
        auth_ttl = auth_ttl.replace(tzinfo=timezone.utc)  # Make auth_ttl timezone-aware

    # Check session validity
    return (
        session.get("user")
        and session.get("user_type")
        and (auth_ttl and auth_ttl > now or await revalidate_session_user())
    )


async def revalidate_session_user():
    user = superdesk.get_resource_service("users").find_one(req=None, _id=session.get("user"))
    if not user:
        clear_user_session()
        return False
    company = get_company(user)
    is_valid = await is_valid_user(user, company)
    if is_valid:
        session["auth_ttl"] = utcnow().replace(tzinfo=None) + SESSION_AUTH_TTL
    return is_valid


def get_user_sections(user: User) -> SectionAllowedMap:
    if not user:
        return {}

    if is_user_admin(user):
        # Admin users should see all sections
        return {section["_id"]: True for section in get_current_app().as_any().sections}

    if user.get("sections"):
        return user["sections"]

    company = get_company(user)
    if company and company.get("sections"):
        return company["sections"]

    return {}


def user_has_section_allowed(user: User, section: Section) -> bool:
    sections = get_user_sections(user)
    if sections:
        return sections.get(section, False)
    return True  # might be False eventually, atm allow access if sections are not set explicitly


def user_can_manage_company(company_id) -> bool:
    if is_current_user_admin() or is_current_user_account_mgr():
        return True
    if is_current_user_company_admin():
        user = get_user()
        if user:
            return str(user.get("company")) == str(company_id) and company_id
    return False


def get_auth_providers() -> Dict[str, AuthProvider]:
    return {provider["_id"]: AuthProvider.get_provider(provider) for provider in get_app_config("AUTH_PROVIDERS")}


def get_company_auth_provider(company: Optional[Company] = None) -> AuthProvider:
    providers = get_auth_providers()

    provider_id = "newshub"
    if company and company.get("auth_provider"):
        provider_id = company.get("auth_provider", "newshub")

    return providers.get(provider_id) or providers["newshub"]


def check_user_has_products(user: User, company_products) -> None:
    """If user has no products and there are no company products abort page rendering."""
    unlimited_products = [p for p in (company_products or []) if not p.get("seats")]
    if (
        not unlimited_products
        and not user.get("products")
        and not (is_current_user_admin() or is_current_user_account_mgr())
    ):
        raise AuthorizationError(
            403, gettext("There is no product associated with your user. Please reach out to your Company Admin.")
        )


def redirect_to_next_url(default_view: str = "wire.index"):
    next_url = session.pop("next_url", None) or url_for(default_view)
    return redirect(next_url)
