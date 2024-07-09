import bson
import flask
import werkzeug
import superdesk

from datetime import datetime, timedelta
from typing import Dict, Optional, TypedDict, Union
from flask import current_app as app
from flask_babel import _
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


def sign_user_by_email(
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

    def redirect_with_error(error_str):
        flask.session.pop("_flashes", None)
        flask.flash(error_str, "danger")
        return flask.redirect(flask.url_for(redirect_on_error, user_error=1))

    if user is None:
        return redirect_with_error(_("User not found"))

    if validate_login_attempt:
        company = get_company(user)
        company_auth_provider = get_company_auth_provider(company)

        if company is None:
            return redirect_with_error(_("No Company assigned"))
        elif not is_company_enabled(user, company):
            return redirect_with_error(_("Company is disabled"))
        elif is_company_expired(user, company):
            return redirect_with_error(_("Company has expired"))
        elif not is_account_enabled(user):
            return redirect_with_error(_("Account is disabled"))
        elif company_auth_provider.type != auth_type:
            return redirect_with_error(
                _("Invalid login type, %(type)s not enabled for your user", type=auth_type.value)
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


def start_user_session(user: User, permanent=False, session=None):
    if session is None:
        session = flask.session
    session["user"] = str(user["_id"])  # str to avoid serialization issues
    session["name"] = "{} {}".format(user.get("first_name"), user.get("last_name"))
    session["user_type"] = user["user_type"]
    session["auth_ttl"] = utcnow().replace(tzinfo=None) + SESSION_AUTH_TTL
    session.permanent = permanent


def clear_user_session(session=None):
    if session is None:
        session = flask.session
    session["user"] = None
    session["name"] = None
    session["user_type"] = None
    session["auth_ttl"] = None
    session["auth_user"] = None


def is_user_admin(user: User) -> bool:
    return user.get("user_type") == UserRole.ADMINISTRATOR.value


def is_current_user_admin() -> bool:
    return flask.session.get("user_type") == UserRole.ADMINISTRATOR.value


def is_current_user_account_mgr() -> bool:
    return flask.session.get("user_type") == UserRole.ACCOUNT_MANAGEMENT.value


def is_current_user_company_admin() -> bool:
    return flask.session.get("user_type") == UserRole.COMPANY_ADMIN.value


def is_current_user(user_id):
    """
    Checks if the current session user is the same as given user id
    """
    return flask.session["user"] == str(user_id)


def send_token(user: User, token_type="validate", update_token=True):
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
            send_validate_account_email(user, token)
        if token_type == "new_account":
            send_new_account_email(user, token)
        elif token_type == "reset_password":
            send_reset_password_email(user, token)
        return True
    return False


class TokenData(TypedDict):
    token: str
    token_expiry_date: datetime


def get_token_data() -> TokenData:
    return {
        "token": get_random_string(),
        "token_expiry_date": utcnow() + timedelta(days=app.config["VALIDATE_ACCOUNT_TOKEN_TIME_TO_LIVE"]),
    }


def add_token_data(user):
    updates = get_token_data()
    user.update(updates)


def is_valid_session():
    """Uses timezone-aware objects to avoid TypeError comparison"""
    now = utcnow()

    return (
        flask.session.get("user")
        and flask.session.get("user_type")
        and (flask.session.get("auth_ttl") and flask.session.get("auth_ttl") > now or revalidate_session_user())
    )


def revalidate_session_user():
    user = superdesk.get_resource_service("users").find_one(req=None, _id=flask.session.get("user"))
    if not user:
        clear_user_session()
        return False
    company = get_company(user)
    is_valid = is_valid_user(user, company)
    if is_valid:
        flask.session["auth_ttl"] = utcnow().replace(tzinfo=None) + SESSION_AUTH_TTL
    return is_valid


def get_user_sections(user: User) -> SectionAllowedMap:
    if not user:
        return {}

    if is_user_admin(user):
        # Admin users should see all sections
        return {section["_id"]: True for section in app.sections}

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
    return {provider["_id"]: AuthProvider.get_provider(provider) for provider in app.config["AUTH_PROVIDERS"]}


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
            403, _("There is no product associated with your user. Please reach out to your Company Admin.")
        )


def redirect_to_next_url(default_view: str = "wire.index"):
    next_url = flask.session.pop("next_url", None) or flask.url_for(default_view)
    return flask.redirect(next_url)
