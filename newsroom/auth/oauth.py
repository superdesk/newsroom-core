import flask
from flask import Blueprint, url_for
from flask_babel import gettext
from authlib.integrations.flask_client import OAuth

import superdesk
from superdesk.utc import utcnow

from newsroom.types import AuthProviderType
from newsroom.template_filters import is_admin
from newsroom.utils import (
    is_company_enabled,
    is_account_enabled,
    is_company_expired,
    get_cached_resource_by_id,
)
from newsroom.limiter import limiter
from newsroom.auth.utils import get_company_auth_provider, redirect_to_next_url

blueprint = Blueprint("oauth", __name__)
oauth = None


def init_app(app):
    global oauth
    oauth = OAuth(app)

    if (app.config.get("GOOGLE_CLIENT_ID") and app.config.get("GOOGLE_CLIENT_SECRET")) or app.config.get(
        "FORCE_ENABLE_GOOGLE_OAUTH"
    ):
        oauth.register(
            "google",
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": " ".join(["openid", "email", "profile"])},
        )
        app.register_blueprint(blueprint)
    else:
        app.config["GOOGLE_LOGIN"] = False


@blueprint.route("/login/google", methods=["GET"])
@limiter.limit("60/hour")
def google_login():
    global oauth
    redirect_uri = url_for(".google_authorized", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@blueprint.route("/login/google_authorized", methods=["GET"])
@limiter.limit("60/hour")
def google_authorized():
    global oauth
    token = oauth.google.authorize_access_token()

    def redirect_with_error(error_str):
        flask.session.pop("_flashes", None)  # remove old messages and just show one message
        flask.flash(error_str, "danger")
        return flask.redirect(url_for("auth.login"))

    if not token:
        return redirect_with_error(gettext("Invalid token"))

    user_data = oauth.google.parse_id_token(token)
    email = user_data["email"]
    if not email:
        return redirect_with_error(gettext("Email not found"))

    # get user by email
    users_service = superdesk.get_resource_service("users")
    user = users_service.find_one(req=None, email=email.lower())
    if not user:
        return redirect_with_error(gettext("User not found"))

    # Check user & company validation
    if not is_admin(user) and not user.get("company"):
        return redirect_with_error(gettext("No Company assigned"))

    company = get_cached_resource_by_id("companies", user.get("company"))

    if not is_company_enabled(user, company):
        return redirect_with_error(gettext("Company is disabled"))

    if is_company_expired(user, company):
        return redirect_with_error(gettext("Company has expired"))

    if not is_account_enabled(user):
        return redirect_with_error(gettext("Account is disabled"))

    auth_provider = get_company_auth_provider(company)
    if auth_provider.type != AuthProviderType.GOOGLE_OAUTH:
        return redirect_with_error(gettext("Invalid login type, Oauth not enabled for your user"))

    # If the user is not yet validated, then validate it now
    if not user.get("is_validated", False):
        users_service.system_update(
            user["_id"],
            {
                "is_validated": True,
                "last_active": utcnow(),
            },
            user,
        )

    # Set flask session information
    flask.session["user"] = str(user["_id"])
    flask.session["name"] = "{} {}".format(user.get("first_name"), user.get("last_name"))
    flask.session["user_type"] = user["user_type"]

    return redirect_to_next_url()
