"""SAML Authentication

To enable:
 - add 'newsroom.auth.saml' to INSTALLED_APPS in settings.py
 - add 'python3-saml==1.14.0' to requirements.txt
 - set SAML_PATH in settings.py to path with config and certificates

"""

import logging
import pathlib
import superdesk

from typing import Dict, List

from urllib.parse import urlparse
from flask import (
    current_app as app,
    request,
    redirect,
    make_response,
    session,
    flash,
    url_for,
    render_template,
    abort,
)
from flask_babel import _
from newsroom.types import UserData
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from newsroom.auth.utils import sign_user_by_email

from . import blueprint


SESSION_NAME_ID = "samlNameId"
SESSION_SESSION_ID = "samlSessionIndex"
SESSION_USERDATA_KEY = "samlUserdata"
SESSION_SAML_CLIENT = "_saml_client"

logger = logging.getLogger(__name__)


def init_saml_auth(req):
    saml_client = session.get(SESSION_SAML_CLIENT)

    if app.config.get("SAML_CLIENTS") and saml_client and saml_client in app.config["SAML_CLIENTS"]:
        logging.info("Using SAML config for %s", saml_client)
        config_path = pathlib.Path(app.config["SAML_BASE_PATH"]).joinpath(saml_client)
        if config_path.exists():
            return OneLogin_Saml2_Auth(req, custom_base_path=str(config_path))
        logger.error("SAML config not found in %s", config_path)
    elif saml_client:
        logging.warn("Unknown SAML client %s", saml_client)

    auth = OneLogin_Saml2_Auth(req, custom_base_path=str(app.config["SAML_PATH"]))
    return auth


def prepare_flask_request(request):
    scheme = request.scheme
    url_data = urlparse(request.url)
    return {
        "https": "on" if scheme == "https" else "off",
        "http_host": request.host,
        "server_port": url_data.port,
        "script_name": request.path,
        "get_data": request.args.copy(),
        "post_data": request.form.copy(),
    }


def get_userdata(nameid: str, saml_data: Dict[str, List[str]]) -> UserData:
    logger.debug("Attributes for %s = %s", nameid, saml_data)

    userdata = UserData(
        email=nameid,
        user_type="internal",
    )

    for saml_key, user_key in app.config["SAML_USER_MAPPING"].items():
        if saml_data.get(saml_key):
            userdata[user_key] = saml_data[saml_key][0]  # type: ignore

    # first we try to find company based on email domain
    domain = nameid.split("@")[-1]
    if domain:
        company = superdesk.get_resource_service("companies").find_one(req=None, auth_domain=domain)
        if company is not None:
            userdata["company"] = company["_id"]

    # then based on preconfigured saml client
    if session.get(SESSION_SAML_CLIENT) and not userdata.get("company"):
        company = superdesk.get_resource_service("companies").find_one(
            req=None, auth_domain=session[SESSION_SAML_CLIENT]
        )
        if company is not None:
            userdata["company"] = company["_id"]

    # last option is global env variable
    if app.config.get("SAML_COMPANY") and not userdata.get("company"):
        company = superdesk.get_resource_service("companies").find_one(req=None, name=app.config["SAML_COMPANY"])
        if company is not None:
            userdata["company"] = company["_id"]
        else:
            logger.warning("Company %s not found", app.config["SAML_COMPANY"])

    return userdata


@blueprint.route("/login/saml", methods=["GET", "POST"])
def saml():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    errors = []

    if "slo" in request.args:
        name_id = None
        session_index = None
        if SESSION_NAME_ID in session:
            name_id = session[SESSION_NAME_ID]
        if SESSION_SESSION_ID in session:
            session_index = session[SESSION_SESSION_ID]
        return redirect(auth.logout(name_id=name_id, session_index=session_index))
    elif "acs" in request.args or request.form:
        auth.process_response()
        errors = auth.get_errors()
        if len(errors) == 0:
            session[SESSION_NAME_ID] = auth.get_nameid().lower()
            session[SESSION_SESSION_ID] = auth.get_session_index()
            session[SESSION_USERDATA_KEY] = auth.get_attributes()
        else:
            logger.error("SAML %s reason=%s", errors, auth.get_last_error_reason())
            flash(_("There was an error when using SSO"), "danger")
            return redirect(url_for("auth.login", user_error=1))
    elif "sls" in request.args:

        def dscb():
            session.clear()

        url = auth.process_slo(delete_session_cb=dscb)
        errors = auth.get_errors()
        if len(errors) == 0:
            if url is not None:
                return redirect(url)

    if session.get(SESSION_NAME_ID):
        return sign_user_by_email(
            session[SESSION_NAME_ID],
            create_missing=True,
            userdata=get_userdata(session[SESSION_NAME_ID], session[SESSION_USERDATA_KEY]),
        )

    return redirect(auth.login())


@blueprint.route("/login/saml_metadata")
def saml_metadata():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = make_response(metadata, 200)
        resp.headers["Content-Type"] = "text/xml"
    else:
        resp = make_response(", ".join(errors), 500)
    return resp


@blueprint.route("/login/<client>", methods=["GET"])
def client_login(client):
    if not client or client not in app.config["SAML_CLIENTS"]:
        return abort(404)
    session[SESSION_SAML_CLIENT] = client
    return render_template("login_client.html", client=client)
