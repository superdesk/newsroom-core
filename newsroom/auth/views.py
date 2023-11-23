from typing import Literal
import flask
import bcrypt
import logging
import google.oauth2.id_token

from bson import ObjectId
from flask import current_app as app, abort
from flask_babel import gettext
from superdesk import get_resource_service
from superdesk.utc import utcnow
from google.auth.transport import requests

from newsroom.types import AuthProviderType
from newsroom.decorator import admin_only, login_required
from newsroom.auth import (
    blueprint,
    get_auth_user_by_email,
    get_company,
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
from newsroom.limiter import limiter

from .token import generate_auth_token, verify_auth_token


logger = logging.getLogger(__name__)


@blueprint.route("/login", methods=["GET", "POST"])
@limiter.limit("60/minute")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if email_has_exceeded_max_login_attempts(form.email.data):
            return flask.render_template("account_locked.html", form=form)

        user = get_user_by_email(form.email.data)
        company = get_company_from_user(user) if user is not None else None

        if is_valid_user(user, company):
            auth_provider = get_company_auth_provider(company)
            if auth_provider.type != AuthProviderType.PASSWORD and not is_admin(user):
                # Password login is not enabled for this user's company, and the user is not an admin
                flask.flash(gettext(f"Invalid login type, please login using '{auth_provider.name}'"), "danger")
            else:
                user_auth = get_auth_user_by_email(user["email"])
                if not _is_password_valid(form.password.data.encode("UTF-8"), user_auth):
                    flask.flash(gettext("Invalid username or password."), "danger")
                else:
                    start_user_session(user, permanent=form.remember_me.data)
                    update_user_last_active(user)
                    return redirect_to_next_url()

    return flask.render_template("login.html", form=form, firebase=app.config.get("FIREBASE_ENABLED"))


def email_has_exceeded_max_login_attempts(email):
    """
    Checks if the user with given email has exceeded maximum number of
    allowed attempts before the successful login.

    It increments the number of attempts and if it exceeds then it disables
    the user account
    """
    if not email:
        return True

    login_attempt = app.cache.get(email)

    if not login_attempt:
        app.cache.set(email, {"attempt_count": 0})
        return False

    login_attempt["attempt_count"] += 1
    app.cache.set(email, login_attempt)
    max_attempt_allowed = app.config["MAXIMUM_FAILED_LOGIN_ATTEMPTS"]

    if login_attempt["attempt_count"] == max_attempt_allowed:
        if login_attempt.get("user_id"):
            get_resource_service("users").patch(id=ObjectId(login_attempt["user_id"]), updates={"is_enabled": False})
        return True

    return login_attempt["attempt_count"] >= max_attempt_allowed


def _is_password_valid(password, user):
    """
    Checks the password of the user
    """
    # user is found so save the id in login attempts
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
def get_login_token():
    email = flask.request.form.get("email")
    password = flask.request.form.get("password")

    if not email or not password:
        abort(400)

    if email_has_exceeded_max_login_attempts(email):
        abort(401, gettext("Exceeded number of allowed login attempts"))

    user = get_auth_user_by_email(email)

    if user is not None and _is_password_valid(password.encode("UTF-8"), user):
        user = get_resource_service("users").find_one(req=None, _id=user["_id"])
        company = get_company_from_user(user)

        if not is_company_enabled(user, company):
            abort(401, gettext("Company account has been disabled."))

        if is_company_expired(user, company):
            abort(401, gettext("Company account has expired."))

        if is_account_enabled(user):
            return generate_auth_token(user)
    else:
        abort(401, gettext("Invalid username or password."))


@blueprint.route("/login/token/<token>", methods=["GET"])
def login_with_token(token):
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
    flask.flash("login", "analytics")
    return flask.redirect(flask.url_for("wire.index"))


@blueprint.route("/logout")
def logout():
    clear_user_session()
    return flask.redirect(flask.url_for("auth.login", logout=1))


@blueprint.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        new_user = form.data
        new_user.pop("csrf_token", None)

        user = get_auth_user_by_email(form.email.data)

        if user is not None:
            flask.flash(gettext("Account already exists."), "danger")
            return flask.redirect(flask.url_for("auth.login"))

        send_new_signup_email(user=new_user)
        return flask.render_template("signup_success.html"), 200
    return flask.render_template(
        "signup.html",
        form=form,
        sitekey=app.config["RECAPTCHA_PUBLIC_KEY"],
        terms=app.config["TERMS_AND_CONDITIONS"],
    )


@blueprint.route("/validate/<token>")
def validate_account(token):
    user = get_resource_service("users").find_one(req=None, token=token)
    if not user:
        flask.abort(404)

    if user.get("is_validated"):
        return flask.redirect(flask.url_for("auth.login"))

    if user.get("token_expiry_date") > utcnow():
        updates = {"is_validated": True, "token": None, "token_expiry_date": None}
        get_resource_service("users").patch(id=ObjectId(user["_id"]), updates=updates)
        flask.flash(gettext("Your account has been validated."), "success")
        return flask.redirect(flask.url_for("auth.login"))

    flask.flash(gettext("Token has expired. Please create a new token"), "danger")
    flask.redirect(flask.url_for("auth.token", token_type="validate"))


@blueprint.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = get_resource_service("users").find_one(req=None, token=token)
    if not user:
        return flask.render_template("password_reset_link_expiry.html")

    form = ResetPasswordForm()
    if form.validate_on_submit():
        updates = {
            "is_validated": True,
            "password": form.new_password.data,
            "token": None,
            "token_expiry_date": None,
        }
        get_resource_service("users").patch(id=ObjectId(user["_id"]), updates=updates)
        flask.flash(gettext("Your password has been changed. Please login again."), "success")
        return flask.redirect(flask.url_for("auth.login"))

    app.cache.delete(user.get("email"))
    return flask.render_template("reset_password.html", form=form, token=token)


@blueprint.route("/token/<token_type>", methods=["GET", "POST"])
def token(token_type: Literal["reset_password", "validate"]):
    """Get token to reset password or validate email."""
    form = TokenForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)
        company = get_company_from_user(user) if user else None
        auth_provider = get_company_auth_provider(company)

        if auth_provider.features.verify_email:
            send_token(user, token_type)

        flask.flash(
            gettext("A reset password token has been sent to your email address."),
            "success",
        )

        return flask.redirect(flask.url_for("auth.login"))

    return flask.render_template(
        "request_token.html", form=form, token_type=token_type, firebase=app.config.get("FIREBASE_ENABLED")
    )


@blueprint.route("/reset_password_done")
def reset_password_confirmation():
    return flask.render_template("request_token_confirm.html")


@blueprint.route("/login_locale", methods=["POST"])
def set_locale():
    locale = flask.request.form.get("locale")
    if locale and locale in app.config["LANGUAGES"]:
        flask.session["locale"] = locale
    return flask.redirect(flask.url_for("auth.login"))


@blueprint.route("/auth/impersonate", methods=["POST"])
@admin_only
def impersonate_user():
    if not flask.session.get("auth_user"):
        flask.session["auth_user"] = flask.session["user"]
    user_id = flask.request.form.get("user")
    assert user_id
    user = get_resource_service("users").find_one(req=None, _id=user_id)
    assert user
    start_user_session(user)
    return flask.redirect(flask.url_for("wire.index"))


@blueprint.route("/auth/impersonate_stop", methods=["POST"])
@login_required
def impersonate_stop():
    assert flask.session.get("auth_user")
    user = get_resource_service("users").find_one(req=None, _id=flask.session.get("auth_user"))
    start_user_session(user)
    flask.session.pop("auth_user")
    return flask.redirect(flask.url_for("settings.app", app_id="users"))


@blueprint.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ResetPasswordForm()
    user = get_user_required()
    company = get_company(user)
    auth_provider = get_company_auth_provider(company)
    form.email.process_data(user["email"])

    if form.validate_on_submit():
        if auth_provider.type == AuthProviderType.FIREBASE:
            if form.data.get("firebase_status"):
                firebase_status = form.data["firebase_status"]
                if firebase_status == "OK":
                    flask.flash(gettext("Your password has been changed."), "success")
                elif firebase_status == "auth/wrong-password":
                    flask.flash(gettext("Wrong current password."), "error")
                else:
                    logger.warning("Unhandled firebase error %s", firebase_status)
                    flask.flash(gettext("Could not change your password. Please contact us for assistance."), "warning")
        elif auth_provider.type == AuthProviderType.PASSWORD:
            updates = {
                "password": form.new_password.data,
            }
            get_resource_service("users").patch(id=ObjectId(user["_id"]), updates=updates)
            flask.flash(gettext("Your password has been changed."), "success")
        else:
            flask.flash(gettext("Change password is not available."), "warning")
        return flask.redirect(flask.url_for("auth.change_password"))

    return flask.render_template(
        "change_password.html", form=form, user=user, firebase=app.config.get("FIREBASE_ENABLED")
    )


@blueprint.route("/firebase_auth_token")
def firebase_auth_token():
    token = flask.request.args.get("token")
    firebase_request_adapter = requests.Request()
    if token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                token,
                audience=app.config["FIREBASE_CLIENT_CONFIG"]["projectId"],
                request=firebase_request_adapter,
            )
        except ValueError as err:
            logger.error(err)
            flask.flash(gettext("User token is not valid"), "danger")
            return flask.redirect(flask.url_for("auth.login", token_error=1))

        email = claims["email"]
        return sign_user_by_email(email, auth_type=AuthProviderType.FIREBASE, validate_login_attempt=True)

    return flask.redirect(flask.url_for("auth.login"))
