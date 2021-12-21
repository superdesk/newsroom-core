import flask
from flask import Blueprint, url_for, render_template
from flask_babel import gettext
from authlib.integrations.flask_client import OAuth

import superdesk
from superdesk.utc import utcnow
from superdesk.utils import get_random_string

from newsroom.template_filters import is_admin
from newsroom.utils import is_company_enabled, is_account_enabled
from newsroom.limiter import limiter

blueprint = Blueprint("oauth", __name__)
oauth = None
AUTHORIZED_TEMPLATE = "oauth_authorized.html"


def init_app(app):
    global oauth
    oauth = OAuth(app)

    if app.config.get("GOOGLE_CLIENT_ID") and app.config.get("GOOGLE_CLIENT_SECRET"):
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
    if not token:
        return render_template(AUTHORIZED_TEMPLATE, data={
            "error": 404,
            "error_str": gettext("Invalid token"),
        })

    user_data = oauth.google.parse_id_token(token)
    email = user_data["email"]
    if not email:
        return render_template(AUTHORIZED_TEMPLATE, data={
            "error": 404,
            "error_str": gettext("Email not found"),
        })

    # get user by email
    users_service = superdesk.get_resource_service("users")
    user = users_service.find_one(req=None, email=email.lower())
    if not user:
        return render_template(AUTHORIZED_TEMPLATE, data={
            "error": 404,
            "error_str": gettext("User not found"),
        })

    # Check user & company validation
    if not is_admin(user) and not user.get("company"):
        flask.session["oauth_error"] = gettext("No Company assigned")
        return render_template(AUTHORIZED_TEMPLATE, data={
            "error": 404,
            "error_str": gettext("No Company assigned"),
        })

    if not is_company_enabled(user):
        return render_template(AUTHORIZED_TEMPLATE, data={
            "error": 404,
            "error_str": gettext("Company is disabled"),
        })

    if not is_account_enabled(user):
        return render_template(AUTHORIZED_TEMPLATE, data={
            "error": 404,
            "error_str": gettext("User account is disabled"),
        })

    # If the user is not yet validated, then validate it now
    if not user.get("is_validated", False):
        users_service.system_update(user["_id"], {
            "is_validated": True,
            "last_active": utcnow(),
        }, user)

    # Set flask session information
    flask.session["user"] = str(user["_id"])
    flask.session["name"] = "{} {}".format(user.get("first_name"), user.get("last_name"))
    flask.session["user_type"] = user["user_type"]

    return render_template(
        AUTHORIZED_TEMPLATE,
        data={
            "email": email,
            "_id": str(user["_id"]),
            "user": str(user["_id"]),
            "token": get_random_string(40),
        }
    )
