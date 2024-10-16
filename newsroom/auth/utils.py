from typing import cast, TypedDict
from datetime import datetime, timedelta

from bson import ObjectId
import werkzeug
from quart_babel import gettext
from uuid import uuid4

from superdesk.core import get_current_app, get_current_async_app, get_app_config, get_current_auth
from superdesk.flask import session, redirect, url_for
from superdesk.core.types import Request
from superdesk.utc import utcnow

from newsroom.types import (
    Product,
    CompanyResource,
    UserResourceModel,
    UserAuthResourceModel,
    UserRole,
    UserData,
    AuthProviderType,
)
from newsroom.flask import flash
from newsroom.core import get_current_wsgi_app
from newsroom.exceptions import AuthorizationError

from .providers import AuthProvider


# how often we should check in db if session
# user is still valid
SESSION_AUTH_TTL = timedelta(minutes=15)


async def sign_user_by_email(
    email: str,
    auth_type: AuthProviderType,
    redirect_on_success: str = "wire.index",
    redirect_on_error: str = "auth.login",
    create_missing: bool = False,
    userdata: UserData | None = None,
    validate_login_attempt: bool = False,
) -> werkzeug.Response:
    from newsroom.users.service import UsersService

    users_service = UsersService()
    user = await users_service.get_by_email(email)
    if user is None and create_missing and userdata is not None:
        user_dict = userdata.copy()
        user_dict["is_enabled"] = True
        user_dict["is_approved"] = True
        await users_service.create([user_dict])
        user = await users_service.get_by_email(email)

    async def redirect_with_error(error_str):
        session.pop("_flashes", None)
        await flash(error_str, "danger")
        return redirect(url_for(redirect_on_error, user_error=1))

    if user is None:
        return await redirect_with_error(gettext("User not found"))

    if validate_login_attempt:
        company = await user.get_company()
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

    await users_service.system_update(
        user.id,
        {
            "is_validated": True,  # in case user was not validated before set it now
            "last_active": utcnow(),
        },
    )

    current_request = get_current_app().get_current_request()
    async_app = get_current_async_app()
    await async_app.auth.start_session(current_request, user)

    return redirect_to_next_url(redirect_on_success)


def redirect_to_next_url(default_view: str = "wire.index"):
    next_url = session.pop("next_url", None) or url_for(default_view)
    return redirect(next_url)


def is_from_request() -> bool:
    try:
        get_current_request()
        return True
    except AuthorizationError:
        return False


def get_current_request() -> Request:
    from superdesk.flask import request as flask_request

    wsgi_app = get_current_wsgi_app()
    request = wsgi_app.get_current_request() or wsgi_app.get_current_request(flask_request)

    if not request:
        raise AuthorizationError(401, gettext("Not from a request"))

    return request


def get_user_from_request(request: Request | None) -> UserResourceModel:
    request = request or get_current_request()
    if request.user is None:
        raise AuthorizationError(401, gettext("Not logged in"))
    elif isinstance(request.user, str):
        # TODO-ASYNC: Fix this, the NewsAPI is setting the token on request.user
        # which is an invalid type
        raise AuthorizationError(401, gettext("Invalid user instance"))

    return cast(UserResourceModel, request.user)


def get_user_or_none_from_request(request: Request | None) -> UserResourceModel | None:
    try:
        return get_user_from_request(request)
    except AuthorizationError:
        return None


def get_user_id_from_request(request: Request | None) -> ObjectId:
    return get_user_from_request(request).id


def get_company_from_request(request: Request | None) -> CompanyResource | None:
    request = request or get_current_request()
    return cast(CompanyResource | None, request.storage.request.get("company_instance", None))


def get_company_or_none_from_request(request: Request | None) -> CompanyResource | None:
    try:
        return get_company_from_request(request)
    except AuthorizationError:
        return None


def is_current_user(user_id: ObjectId | str, request: Request | None = None) -> bool:
    return get_user_from_request(request).id == ObjectId(user_id)


def get_current_user_sections(request: Request | None) -> dict[str, bool]:
    return get_user_sections(get_user_from_request(request), get_company_from_request(request))


def get_user_sections(user: UserResourceModel | None, company: CompanyResource | None) -> dict[str, bool]:
    if not user:
        return {}
    elif user.user_type == UserRole.ADMINISTRATOR:
        return {section["_id"]: True for section in get_current_wsgi_app().sections}
    elif user.sections:
        return user.sections
    elif company and company.sections:
        return company.sections
    return {}


def get_auth_providers() -> dict[str, "AuthProvider"]:
    return {provider["_id"]: AuthProvider.get_provider(provider) for provider in get_app_config("AUTH_PROVIDERS")}


def get_company_auth_provider(company: CompanyResource | None) -> "AuthProvider":
    providers = get_auth_providers()
    provider_id = "newshub"
    if company and company.auth_provider:
        provider_id = company.auth_provider

    return providers.get(provider_id) or providers["newshub"]


class TokenData(TypedDict):
    token: str
    token_expiry_date: datetime


def get_token_data() -> TokenData:
    return {
        "token": str(uuid4()),
        "token_expiry_date": utcnow() + timedelta(days=get_app_config("VALIDATE_ACCOUNT_TOKEN_TIME_TO_LIVE")),
    }


def add_token_data(user: UserAuthResourceModel):
    for key, val in get_token_data().items():
        setattr(user, key, val)


async def send_token(user: UserAuthResourceModel | None, token_type: str = "validate", update_token=True) -> bool:
    from newsroom.users import UsersAuthService

    if user is None or not user.is_enabled:
        return False
    elif token_type == "validate" and user.is_validated:
        return False

    token = user.token
    if update_token:
        updates = get_token_data()
        await UsersAuthService().system_update(user.id, updates)
        token = updates["token"]

    assert isinstance(token, str)

    user_dict = user.to_dict()
    if token_type == "validate":
        await send_validate_account_email(user_dict, token)
    if token_type == "new_account":
        await send_new_account_email(user_dict, token)
    elif token_type == "reset_password":
        await send_reset_password_email(user_dict, token)
    else:
        return False
    return True


def is_company_enabled(user: UserResourceModel | None, company: CompanyResource | None) -> bool:
    """
    Checks if the company of the user is enabled
    """
    if user and not user.company:
        # there's no company assigned return true for admin user else false
        return True if user.is_admin() else False

    return False if not company else company.is_enabled


def is_company_expired(user: UserResourceModel | None, company: CompanyResource | None) -> bool:
    if get_app_config("ALLOW_EXPIRED_COMPANY_LOGINS"):
        return False
    elif user and not user.company:
        return False if user.is_admin() else True
    elif company and company.expiry_date:
        return company.expiry_date.replace(tzinfo=None) < datetime.now()

    return False


async def is_account_enabled(user: UserResourceModel):
    """
    Checks if user account is active and approved
    """
    if not user.is_enabled:
        await flash(gettext("Account is disabled"), "danger")
        return False

    if not user.is_approved:
        account_created = user.created

        approve_expiration = utcnow() + timedelta(days=-get_app_config("NEW_ACCOUNT_ACTIVE_DAYS", 14))
        if not account_created or account_created < approve_expiration:
            await flash(gettext("Account has not been approved"), "danger")
            return False

    return True


async def is_valid_user(user: UserResourceModel | None, company: CompanyResource | None) -> bool:
    """Validate if user is valid and should be able to login to the system."""
    if not user:
        await flash(gettext("Invalid username or password."), "danger")
        return False

    current_request = get_current_request()
    current_request.storage.session.pop("_flashes", None)  # remove old messages and just show one message

    if not user.is_admin() and not company:
        await flash(gettext("Insufficient Permissions. Access denied."), "danger")
        return False

    if not await is_account_enabled(user):
        await flash(gettext("Account is disabled"), "danger")
        return False

    if not is_company_enabled(user, company):
        await flash(gettext("Company account has been disabled."), "danger")
        return False

    if is_company_expired(user, company):
        await flash(gettext("Company account has expired."), "danger")
        return False

    return True


# TODO-ASYNC: Remove this once everything is async
async def is_valid_session() -> bool:
    """Uses timezone-aware objects to avoid TypeError comparison"""
    # Get the current UTC time as a timezone-aware datetime

    try:
        request = get_current_request()
        return await get_current_auth().authenticate(request) is None
    except AuthorizationError:
        pass

    await clear_user_session()
    return False


async def clear_user_session(request: Request | None = None):
    try:
        await get_current_auth().stop_session(request or get_current_request())
    except AuthorizationError:
        pass


def check_user_has_products(user: UserResourceModel, company_products: list[Product]) -> None:
    """If user has no products and there are no company products abort page rendering."""
    unlimited_products = company_products or []
    if not unlimited_products and not user.products and not (user.is_admin() or user.is_account_manager()):
        raise AuthorizationError(
            403, gettext("There is no product associated with your user. Please reach out to your Company Admin.")
        )


from newsroom.email import send_validate_account_email, send_reset_password_email, send_new_account_email  # noqa: E402
