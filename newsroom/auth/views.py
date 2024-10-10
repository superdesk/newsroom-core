import re
import bcrypt
import logging
import google.oauth2.id_token

from typing import Literal, Any
from datetime import timedelta

from pydantic import BaseModel
from bson import ObjectId
from google.auth.transport import requests
from quart_babel import gettext

from superdesk.core import get_app_config, get_current_app, get_current_async_app, get_current_auth
from superdesk.core.types import Request
from superdesk.core.web import EndpointGroup
from superdesk.core.module import Module
from superdesk.flask import render_template, url_for
from superdesk import get_resource_service
from superdesk.utc import utcnow

from newsroom.flask import flash
from newsroom.types import AuthProviderType, UserAuthResourceModel, User, UserRole
from newsroom.auth.forms import SignupForm, LoginForm, TokenForm, ResetPasswordForm
from newsroom.auth.utils import (
    redirect_to_next_url,
    sign_user_by_email,
)
from newsroom.email import send_new_signup_email
from newsroom.limiter import rate_limit
from newsroom.users import UsersService, UsersAuthService
from newsroom.companies.companies_async import CompanyService

from .utils import (
    get_user_from_request,
    get_user_or_none_from_request,
    get_company_from_request,
    is_valid_user,
    get_company_auth_provider,
    send_token,
    is_company_enabled,
    is_account_enabled,
    is_company_expired,
)
from .auth_rules import admin_only
from .token import generate_auth_token, verify_auth_token


blueprint = EndpointGroup("auth", __name__)
logger = logging.getLogger(__name__)


@blueprint.endpoint("/login", methods=["GET", "POST"], auth=False)
@rate_limit(60, timedelta(minutes=1))
async def login(req: Request):
    form = await LoginForm.create_form()

    if req.user and req.user.email == form.email.data:
        return redirect_to_next_url()

    if await form.validate_on_submit():
        # login form has been submitted, so we should stop existing session, if any
        auth = get_current_auth()
        await auth.stop_session(req)

        if email_has_exceeded_max_login_attempts(form.email.data):
            return await render_template("account_locked.html", form=form)

        user = await UsersAuthService().get_by_email(form.email.data)
        company = await user.get_company() if user else None

        if user is None:
            await flash(gettext("Invalid username or password."), "danger")
        elif await is_valid_user(user, company):
            auth_provider = get_company_auth_provider(company)
            firebase_status = form.firebase_status.data
            if (
                auth_provider.type == AuthProviderType.FIREBASE
                and firebase_status
                and firebase_status
                in (
                    "auth/user-disabled",
                    "auth/user-not-found",
                    "auth/wrong-password",
                )
            ):
                await flash(gettext("Invalid username or password."), "danger")
            elif auth_provider.type == AuthProviderType.FIREBASE and firebase_status:
                await log_firebase_unexpected_error(firebase_status)
            elif auth_provider.type != AuthProviderType.PASSWORD and not user.is_admin():
                # Password login is not enabled for this user's company, and the user is not an admin
                await flash(gettext(f"Invalid login type, please login using '{auth_provider.name}'"), "danger")
            else:
                if not _is_password_valid(form.password.data.encode("UTF-8"), user):
                    await flash(gettext("Invalid username or password."), "danger")
                else:
                    await auth.start_session(req, user, permanent=form.remember_me.data)
                    return redirect_to_next_url()

    return await render_template("login.html", form=form, firebase=get_app_config("FIREBASE_ENABLED"))


def email_has_exceeded_max_login_attempts(email):
    """
    Checks if the user with given email has exceeded maximum number of
    allowed attempts before the successful login.

    It increments the number of attempts and if it exceeds then it disables
    the user account
    """
    if not email:
        return True

    app = get_current_app().as_any()
    login_attempt = app.cache.get(email)

    if not login_attempt:
        app.cache.set(email, {"attempt_count": 0})
        return False

    login_attempt["attempt_count"] += 1
    app.cache.set(email, login_attempt)
    max_attempt_allowed = get_app_config("MAXIMUM_FAILED_LOGIN_ATTEMPTS")

    if login_attempt["attempt_count"] == max_attempt_allowed:
        if login_attempt.get("user_id"):
            get_resource_service("auth_user").patch(
                id=ObjectId(login_attempt["user_id"]), updates={"is_enabled": False}
            )
        return True

    return login_attempt["attempt_count"] >= max_attempt_allowed


def _is_password_valid(password: bytes, user: UserAuthResourceModel):
    """
    Checks the password of the user
    """
    # user is found so save the id in login attempts
    if not user.password:
        return False

    app = get_current_app().as_any()
    previous_login_attempt = app.cache.get(user.email) or {}
    previous_login_attempt["user_id"] = user.id
    app.cache.set(user.email, previous_login_attempt)

    try:
        hashed = user.password.encode("UTF-8")
    except (Exception, AttributeError, KeyError):
        return False

    try:
        if bcrypt.checkpw(password, hashed):
            # login successful so remove the login attempt check record
            app.cache.delete(user.email)
            return True
    except (TypeError, ValueError):
        return False

    return False


# this could be rate limited to a specific ip address
@blueprint.endpoint("/login/token/", methods=["POST"], auth=False)
async def get_login_token(req: Request):
    form = await req.get_form()
    email = form.get("email")
    password = form.get("password")

    if not email or not password:
        return await req.abort(400)

    if email_has_exceeded_max_login_attempts(email):
        return await req.abort(401, gettext("Exceeded number of allowed login attempts"))

    user_auth = await UsersAuthService().get_by_email(email)

    if user_auth is not None and _is_password_valid(password.encode("UTF-8"), user_auth):
        user = await UsersService().find_by_id(user_auth.id)
        company = await user.get_company()

        if not is_company_enabled(user, company):
            return await req.abort(401, gettext("Company account has been disabled."))

        if is_company_expired(user, company):
            return await req.abort(401, gettext("Company account has expired."))

        if await is_account_enabled(user):
            return generate_auth_token(user)
    else:
        return await req.abort(401, gettext("Invalid username or password."))


class LoginTokenRouteArgs(BaseModel):
    token: str | None = None


@blueprint.endpoint("/login/token/<token>", methods=["GET"], auth=False)
async def login_with_token(args: LoginTokenRouteArgs, params: None, req: Request) -> Any:
    if not args.token:
        return await req.abort(401, gettext("Invalid token"))

    data = verify_auth_token(args.token)
    if not data:
        return await req.abort(401, gettext("Invalid token"))

    user = await UsersService().find_by_id(data["id"])
    if not user:
        return await req.abort(401, gettext("Invalid user"))

    await get_current_async_app().auth.start_session(req, user)
    await flash("login", "analytics")
    return req.redirect(url_for("wire.index"))


@blueprint.endpoint("/logout", auth=False)
async def logout(req: Request):
    await get_current_async_app().auth.stop_session(req)
    return req.redirect(url_for("auth.login", logout=1))


@blueprint.endpoint("/signup", methods=["GET", "POST"], auth=False)
async def signup(req: Request):
    if not get_app_config("SIGNUP_EMAIL_RECIPIENTS"):
        return await req.abort(404)
    app = get_current_app().as_any()
    form = await (app.signup_form_class or SignupForm).create_form()

    if len(app.countries):
        form.country.choices += [(item.get("value"), item.get("text")) for item in app.countries]

    company_types = get_app_config("COMPANY_TYPES") or []
    if len(company_types):
        form.company_type.choices += [(item.get("id"), item.get("name")) for item in company_types]

    if await form.validate_on_submit():
        user_auth = await UsersAuthService().get_by_email(form.email.data)
        if user_auth is not None:
            await flash(gettext("Account already exists."), "danger")
            return req.redirect(url_for("auth.login"))

        company_service = CompanyService()
        company_name = re.escape(form.company.data)
        regex = re.compile(f"^{company_name}$", re.IGNORECASE)
        company = await company_service.find_one(name=regex)
        company_dict = company.to_dict() if company else None
        is_new_company = company_dict is None

        if is_new_company:
            enabled_products = get_resource_service("products").get(req=None, lookup={"is_enabled": True})
            company_dict = {
                "name": form.company.data,
                "contact_name": form.first_name.data + " " + form.last_name.data,
                "contact_email": form.email.data,
                "phone": form.phone.data,
                "country": form.country.data,
                "company_type": form.company_type.data,
                "url": form.company_url.data,
                "company_size": form.company_size.data,
                "referred_by": form.referred_by.data,
                "is_enabled": False,
                "is_approved": False,
                "sections": {section["_id"]: True for section in app.sections},
                "products": [
                    {"_id": product.get("_id"), "seats": 0, "section": product.get("product_type")}
                    for product in enabled_products
                ],
            }
            company_dict["_id"] = (await company_service.create([company_dict]))[0]

        user_service = UsersService()
        new_user_dict: User = {
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "email": form.email.data,
            "phone": form.phone.data,
            "role": form.occupation.data,
            "country": form.country.data,
            "company": company_dict["_id"],
            "is_validated": False,
            "is_enabled": False,
            "is_approved": False,
            "sections": {section["_id"]: True for section in app.sections},
            "user_type": UserRole.PUBLIC.value,
        }
        new_user_dict["_id"] = (await user_service.create([new_user_dict]))[0]
        await send_new_signup_email(company_dict, new_user_dict, is_new_company)

        return await render_template("signup_success.html"), 200
    return await render_template(
        "signup.html",
        form=form,
        sitekey=get_app_config("RECAPTCHA_PUBLIC_KEY"),
        terms=get_app_config("TERMS_AND_CONDITIONS"),
    )


@blueprint.endpoint("/validate/<token>", auth=False)
async def validate_account(args: LoginTokenRouteArgs, params: None, req: Request) -> Any:
    users_service = UsersAuthService()
    user = await users_service.find_one(token=args.token)
    if not user:
        return await req.abort(404)

    if user.is_validated:
        return req.redirect(url_for("auth.login"))

    if user.token_expiry_date and user.token_expiry_date > utcnow():
        updates = {"is_validated": True, "token": None, "token_expiry_date": None}
        await users_service.update(user.id, updates)
        await flash(gettext("Your account has been validated."), "success")
        return req.redirect(url_for("auth.login"))

    await flash(gettext("Token has expired. Please create a new token"), "danger")
    return req.redirect(url_for("auth.token", token_type="validate"))


@blueprint.endpoint("/reset_password/<token>", methods=["GET", "POST"], auth=False)
async def reset_password(args: LoginTokenRouteArgs, params: None, req: Request) -> Any:
    users_service = UsersAuthService()
    user = await users_service.find_one(token=args.token)
    if not user:
        return await render_template("password_reset_link_expiry.html")

    form = await ResetPasswordForm.create_form()
    if await form.validate_on_submit():
        updates = {
            "is_validated": True,
            "password": form.new_password.data,
            "token": None,
            "token_expiry_date": None,
        }
        await users_service.update(user.id, updates=updates)
        await flash(gettext("Your password has been changed. Please login again."), "success")

        if get_user_or_none_from_request(None) is not None:  # user is authenticated already
            return redirect_to_next_url()

        return req.redirect(url_for("auth.login"))

    get_current_app().as_any().cache.delete(user.email)
    return await render_template("reset_password.html", form=form, token=args.token)


class LoginTokenTypeRouteArgs(BaseModel):
    token_type: Literal["reset_password", "validate"]


@blueprint.endpoint("/token/<token_type>", methods=["GET", "POST"], auth=False)
async def token(args: LoginTokenTypeRouteArgs, params: None, req: Request) -> Any:
    """Get token to reset password or validate email."""
    form = await TokenForm.create_form()
    if await form.validate_on_submit():
        user = await UsersAuthService().get_by_email(form.email.data)
        company = await user.get_company() if user else None
        auth_provider = get_company_auth_provider(company)

        assert user

        if auth_provider.features["verify_email"]:
            await send_token(user, args.token_type)

        await flash(
            gettext("A reset password token has been sent to your email address."),
            "success",
        )

        return req.redirect(url_for("auth.login"))

    return await render_template(
        "request_token.html", form=form, token_type=args.token_type, firebase=get_app_config("FIREBASE_ENABLED")
    )


@blueprint.endpoint("/reset_password_done", auth=False)
async def reset_password_confirmation():
    return await render_template("request_token_confirm.html")


@blueprint.endpoint("/login_locale", methods=["POST"], auth=False)
async def set_locale(req: Request):
    locale = (await req.get_form()).get("locale")
    if locale and locale in get_app_config("LANGUAGES"):
        req.storage.session.set("locale", locale)
    return req.redirect(url_for("auth.login"))


@blueprint.endpoint("/auth/impersonate", methods=["POST"], auth=[admin_only])
async def impersonate_user(req: Request):
    if not req.storage.session.get("auth_user"):
        user = get_user_from_request(req)
        req.storage.session.set("auth_user", str(user.id))

    user_id = (await req.get_form()).get("user")
    assert user_id
    user = await UsersService().find_by_id(user_id)
    assert user
    await get_current_async_app().auth.start_session(req, user)
    return req.redirect(url_for("wire.index"))


@blueprint.endpoint("/auth/impersonate_stop", methods=["POST"])
async def impersonate_stop(req: Request):
    auth_user = req.storage.session.get("auth_user")
    assert auth_user

    user = await UsersService().find_by_id(auth_user)
    await get_current_async_app().auth.start_session(req, user)
    req.storage.session.pop("auth_user")
    return req.redirect(url_for("settings.settings_app", app_id="users"))


@blueprint.endpoint("/change_password", methods=["GET", "POST"])
async def change_password(req: Request):
    form = await ResetPasswordForm.create_form()
    user = get_user_from_request(req)
    company = get_company_from_request(req)

    auth_provider = get_company_auth_provider(company)
    form.email.process_data(user.email)

    if await form.validate_on_submit():
        if auth_provider.type == AuthProviderType.FIREBASE:
            if form.data.get("firebase_status"):
                firebase_status = form.data["firebase_status"]
                if firebase_status == "OK":
                    await flash(gettext("Your password has been changed."), "success")
                elif firebase_status == "auth/wrong-password":
                    await flash(gettext("Current password invalid."), "danger")
                else:
                    await log_firebase_unexpected_error(firebase_status)
                return req.redirect(url_for("auth.change_password"))
        elif auth_provider.type == AuthProviderType.PASSWORD:
            user_auth = await UsersAuthService().get_by_email(user.email)
            if user_auth is None:
                await flash(gettext("Invalid username or password."), "danger")
            elif not _is_password_valid(form.old_password.data.encode("UTF-8"), user_auth):
                await flash(gettext("Invalid username or password."), "danger")
            else:
                updates = {"password": form.new_password.data}
                await UsersAuthService().update(user.id, updates=updates)
                await flash(gettext("Your password has been changed."), "success")
                return req.redirect(url_for("auth.change_password"))
        else:
            await flash(gettext("Change password is not available."), "warning")

    return await render_template(
        "change_password.html", form=form, user=user.to_dict(), firebase=get_app_config("FIREBASE_ENABLED")
    )


@blueprint.endpoint("/firebase_auth_token", auth=False)
async def firebase_auth_token(args: None, params: LoginTokenRouteArgs, req: Request):
    firebase_request_adapter = requests.Request()
    if params.token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                params.token,
                audience=get_app_config("FIREBASE_CLIENT_CONFIG")["projectId"],
                request=firebase_request_adapter,
            )
        except ValueError as err:
            logger.error(err)
            await flash(gettext("User token is not valid"), "danger")
            return req.redirect(url_for("auth.login", token_error=1))

        email = claims["email"]
        return await sign_user_by_email(email, auth_type=AuthProviderType.FIREBASE, validate_login_attempt=True)

    return req.redirect(url_for("auth.login"))


async def log_firebase_unexpected_error(firebase_status: str):
    logger.warning("Unhandled firebase error %s", firebase_status)
    await flash(gettext("Could not change your password. Please contact us for assistance."), "warning")


module = Module(
    name="newsroom.auth.views",
    endpoints=[blueprint],
)
