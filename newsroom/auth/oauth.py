from datetime import timedelta

from quart_babel import gettext
from authlib.integrations.flask_client import OAuth

from superdesk.core import get_current_app, get_current_async_app
from superdesk.flask import Blueprint, url_for, session, redirect
from superdesk.utc import utcnow

from newsroom.flask import flash
from newsroom.types import AuthProviderType
from newsroom.auth.utils import is_company_enabled, is_account_enabled, is_company_expired
from newsroom.users import UsersService

from newsroom.limiter import rate_limit
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
@rate_limit(60, timedelta(hours=1))
def google_login():
    global oauth
    redirect_uri = url_for(".google_authorized", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@blueprint.route("/login/google_authorized", methods=["GET"])
@rate_limit(60, timedelta(hours=1))
async def google_authorized():
    global oauth
    token = oauth.google.authorize_access_token()

    async def redirect_with_error(error_str):
        session.pop("_flashes", None)  # remove old messages and just show one message
        await flash(error_str, "danger")
        return redirect(url_for("auth.login"))

    if not token:
        return await redirect_with_error(gettext("Invalid token"))

    user_data = oauth.google.parse_id_token(token)
    email = user_data["email"]
    if not email:
        return await redirect_with_error(gettext("Email not found"))

    # get user by email
    users_service = UsersService()
    user = await users_service.get_by_email(email.lower())
    if not user:
        return await redirect_with_error(gettext("User not found"))

    # Check user & company validation
    if not user.is_admin() and not user.company:
        return await redirect_with_error(gettext("No Company assigned"))

    company = await user.get_company()

    if not is_company_enabled(user, company):
        return await redirect_with_error(gettext("Company is disabled"))

    if is_company_expired(user, company):
        return await redirect_with_error(gettext("Company has expired"))

    if not await is_account_enabled(user):
        return await redirect_with_error(gettext("Account is disabled"))

    auth_provider = get_company_auth_provider(company)
    if auth_provider.type != AuthProviderType.GOOGLE_OAUTH:
        return await redirect_with_error(gettext("Invalid login type, Oauth not enabled for your user"))

    # If the user is not yet validated, then validate it now
    if not user.is_validated:
        await users_service.system_update(
            user["_id"],
            {
                "is_validated": True,
                "last_active": utcnow(),
            },
        )

    # Set flask session information
    await get_current_async_app().auth.start_session(
        get_current_app().get_current_request(),
        user,
        company=company,
    )

    return redirect_to_next_url()
