import re
import bcrypt
import logging
import google.oauth2.id_token

from typing import Literal
from datetime import timedelta

from bson import ObjectId
from google.auth.transport import requests
from quart_babel import gettext

from superdesk.core import get_app_config, get_current_app
from superdesk.flask import abort, Blueprint, render_template, request, url_for, redirect, session
from superdesk import get_resource_service
from superdesk.utc import utcnow

from newsroom.flask import flash
from newsroom.types import AuthProviderType
from newsroom.decorator import admin_only, login_required
from newsroom.auth import (
    get_auth_user_by_email,
    get_company,
    get_user,
    get_user_by_email,
    get_company_from_user,
    get_user_required,
)
from newsroom.auth.forms import SignupForm, LoginForm, TokenForm, ResetPasswordForm
from newsroom.auth.utils import (
    clear_user_session,
    redirect_to_next_url,
    sign_user_by_email,
    start_user_session,
    send_token,
    get_company_auth_provider,
    is_valid_session,
)
from newsroom.utils import (
    is_company_enabled,
    is_account_enabled,
    is_company_expired,
    is_valid_user,
    update_user_last_active,
    is_admin,
)
from newsroom.email import send_new_signup_email
from newsroom.limiter import rate_limit
from newsroom.users.service import UsersService

from .token import generate_auth_token, verify_auth_token


blueprint = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)


@blueprint.route("/login", methods=["GET", "POST"])
@rate_limit(60, timedelta(minutes=1))
async def login():
    if await is_valid_session():
        # If user has already logged in, then redirect them to the next page
        # which defaults to the home page
        return redirect_to_next_url()

    form = await LoginForm.create_form()
    if await form.validate_on_submit():
        if email_has_exceeded_max_login_attempts(form.email.data):
            return await render_template("account_locked.html", form=form)

        user = get_user_by_email(form.email.data)
        company = get_company_from_user(user) if user is not None else None

        if await is_valid_user(user, company):
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
            elif auth_provider.type != AuthProviderType.PASSWORD and not is_admin(user):
                # Password login is not enabled for this user's company, and the user is not an admin
                await flash(gettext(f"Invalid login type, please login using '{auth_provider.name}'"), "danger")
            else:
                user_auth = get_auth_user_by_email(user["email"])
                if not _is_password_valid(form.password.data.encode("UTF-8"), user_auth):
                    await flash(gettext("Invalid username or password."), "danger")
                else:
                    start_user_session(user, permanent=form.remember_me.data)
                    update_user_last_active(user)
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


def _is_password_valid(password, user):
    """
    Checks the password of the user
    """
    # user is found so save the id in login attempts
    app = get_current_app().as_any()
    previous_login_attempt = app.cache.get(user.get("email")) or {}
    previous_login_attempt["user_id"] = user.get("_id")
    app.cache.set(user.get("email"), previous_login_attempt)

    try:
        hashed = user["password"].encode("UTF-8")
    except (AttributeError, KeyError):
        return False

    try:
        if not bcrypt.checkpw(password, hashed):
            return False
    except (TypeError, ValueError):
        return False

    # login successful so remove the login attempt check record
    app.cache.delete(user.get("email"))
    return True


# this could be rate limited to a specific ip address
@blueprint.route("/login/token/", methods=["POST"])
async def get_login_token():
    email = (await request.form).get("email")
    password = (await request.form).get("password")

    if not email or not password:
        abort(400)

    if email_has_exceeded_max_login_attempts(email):
        abort(401, gettext("Exceeded number of allowed login attempts"))

    user = get_auth_user_by_email(email)

    if user is not None and _is_password_valid(password.encode("UTF-8"), user):
        user_dict = {}
        user = await UsersService().find_by_id(user["_id"])
        if user:
            user_dict = user.model_dump(by_alias=True)

        company = get_company_from_user(user_dict)

        if not is_company_enabled(user_dict, company):
            abort(401, gettext("Company account has been disabled."))

        if is_company_expired(user_dict, company):
            abort(401, gettext("Company account has expired."))

        if await is_account_enabled(user_dict):
            return generate_auth_token(user_dict)
    else:
        abort(401, gettext("Invalid username or password."))


@blueprint.route("/login/token/<token>", methods=["GET"])
async def login_with_token(token):
    if not token:
        abort(401, gettext("Invalid token"))

    data = verify_auth_token(token)
    if not data:
        abort(401, gettext("Invalid token"))

    user_data = {
        "_id": data["id"],
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "user_type": data["user_type"],
    }

    start_user_session(user_data)
    await flash("login", "analytics")
    return redirect(url_for("wire.index"))


@blueprint.route("/logout")
def logout():
    clear_user_session()
    return redirect(url_for("auth.login", logout=1))


@blueprint.route("/signup", methods=["GET", "POST"])
async def signup():
    app = get_current_app().as_any()
    form = await (app.signup_form_class or SignupForm).create_form()
    if len(app.countries):
        form.country.choices += [(item.get("value"), item.get("text")) for item in app.countries]

    company_types = get_app_config("COMPANY_TYPES") or []
    if len(company_types):
        form.company_type.choices += [(item.get("id"), item.get("name")) for item in company_types]

    if await form.validate_on_submit():
        user = get_auth_user_by_email(form.email.data)
        if user is not None:
            await flash(gettext("Account already exists."), "danger")
            return redirect(url_for("auth.login"))

        company_service = get_resource_service("companies")
        company_name = re.escape(form.company.data)
        regex = re.compile(f"^{company_name}$", re.IGNORECASE)
        company = company_service.find_one(req=None, name=regex)
        is_new_company = company is None

        if is_new_company:
            enabled_products = get_resource_service("products").get(req=None, lookup={"is_enabled": True})
            company = {
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
            ids = company_service.post([company])
            company["_id"] = ids[0]

        user_service = UsersService()
        new_user = {
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "email": form.email.data,
            "phone": form.phone.data,
            "role": form.occupation.data,
            "country": form.country.data,
            "company": company["_id"],
            "is_validated": False,
            "is_enabled": False,
            "is_approved": False,
            "sections": {section["_id"]: True for section in app.sections},
        }
        await user_service.create([new_user])
        await send_new_signup_email(company, new_user, is_new_company)
        return await render_template("signup_success.html"), 200
    return await render_template(
        "signup.html",
        form=form,
        sitekey=get_app_config("RECAPTCHA_PUBLIC_KEY"),
        terms=get_app_config("TERMS_AND_CONDITIONS"),
    )


@blueprint.route("/validate/<token>")
async def validate_account(token):
    user = get_resource_service("users").find_one(req=None, token=token)
    if not user:
        abort(404)

    if user.get("is_validated"):
        return redirect(url_for("auth.login"))

    if user.get("token_expiry_date") > utcnow():
        updates = {"is_validated": True, "token": None, "token_expiry_date": None}
        await UsersService().update(user["_id"], updates)
        await flash(gettext("Your account has been validated."), "success")
        return redirect(url_for("auth.login"))

    await flash(gettext("Token has expired. Please create a new token"), "danger")
    redirect(url_for("auth.token", token_type="validate"))


@blueprint.route("/reset_password/<token>", methods=["GET", "POST"])
async def reset_password(token):
    user = get_resource_service("users").find_one(req=None, token=token)
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
        await UsersService().update(user["_id"], updates=updates)
        await flash(gettext("Your password has been changed. Please login again."), "success")

        if get_user() is not None:  # user is authenticated already
            return redirect_to_next_url()

        return redirect(url_for("auth.login"))

    get_current_app().as_any().cache.delete(user.get("email"))
    return await render_template("reset_password.html", form=form, token=token)


@blueprint.route("/token/<token_type>", methods=["GET", "POST"])
async def token(token_type: Literal["reset_password", "validate"]):
    """Get token to reset password or validate email."""
    form = await TokenForm.create_form()
    if await form.validate_on_submit():
        user = get_user_by_email(form.email.data)
        company = get_company_from_user(user) if user else None
        auth_provider = get_company_auth_provider(company)

        assert user

        if auth_provider.features["verify_email"]:
            await send_token(user, token_type)

        await flash(
            gettext("A reset password token has been sent to your email address."),
            "success",
        )

        return redirect(url_for("auth.login"))

    return await render_template(
        "request_token.html", form=form, token_type=token_type, firebase=get_app_config("FIREBASE_ENABLED")
    )


@blueprint.route("/reset_password_done")
async def reset_password_confirmation():
    return await render_template("request_token_confirm.html")


@blueprint.route("/login_locale", methods=["POST"])
async def set_locale():
    locale = (await request.form).get("locale")
    if locale and locale in get_app_config("LANGUAGES"):
        session["locale"] = locale
    return redirect(url_for("auth.login"))


@blueprint.route("/auth/impersonate", methods=["POST"])
@admin_only
async def impersonate_user():
    if not session.get("auth_user"):
        session["auth_user"] = session["user"]
    user_id = (await request.form).get("user")
    assert user_id
    user = await UsersService().find_by_id(user_id)
    assert user
    start_user_session(user)
    return redirect(url_for("wire.index"))


@blueprint.route("/auth/impersonate_stop", methods=["POST"])
@login_required
async def impersonate_stop():
    assert session.get("auth_user")
    user = await UsersService().find_by_id(session.get("auth_user"))
    start_user_session(user)
    session.pop("auth_user")
    return redirect(url_for("settings.app", app_id="users"))


@blueprint.route("/change_password", methods=["GET", "POST"])
@login_required
async def change_password():
    form = await ResetPasswordForm.create_form()
    user = get_user_required()
    company = get_company(user)
    auth_provider = get_company_auth_provider(company)
    form.email.process_data(user["email"])

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
                return redirect(url_for("auth.change_password"))
        elif auth_provider.type == AuthProviderType.PASSWORD:
            user_auth = get_auth_user_by_email(user["email"])
            if not _is_password_valid(form.old_password.data.encode("UTF-8"), user_auth):
                await flash(gettext("Current password invalid."), "danger")
            else:
                updates = {"password": form.new_password.data}
                await UsersService().update(user["_id"], updates=updates)
                await flash(gettext("Your password has been changed."), "success")
                return redirect(url_for("auth.change_password"))
        else:
            await flash(gettext("Change password is not available."), "warning")

    return await render_template(
        "change_password.html", form=form, user=user, firebase=get_app_config("FIREBASE_ENABLED")
    )


@blueprint.route("/firebase_auth_token")
async def firebase_auth_token():
    token = request.args.get("token")
    firebase_request_adapter = requests.Request()
    if token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                token,
                audience=get_app_config("FIREBASE_CLIENT_CONFIG")["projectId"],
                request=firebase_request_adapter,
            )
        except ValueError as err:
            logger.error(err)
            await flash(gettext("User token is not valid"), "danger")
            return redirect(url_for("auth.login", token_error=1))

        email = claims["email"]
        return await sign_user_by_email(email, auth_type=AuthProviderType.FIREBASE, validate_login_attempt=True)

    return redirect(url_for("auth.login"))


async def log_firebase_unexpected_error(firebase_status: str):
    logger.warning("Unhandled firebase error %s", firebase_status)
    await flash(gettext("Could not change your password. Please contact us for assistance."), "warning")
