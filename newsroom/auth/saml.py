"""SAML Authentication

To enable:
 - add 'newsroom.auth.saml' to INSTALLED_APPS in settings.py
 - add 'python3-saml==1.14.0' to requirements.txt
 - set SAML_PATH in settings.py to path with config and certificates

"""

import enum
import logging
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
)
from flask_babel import _
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from newsroom.auth.utils import UserData, sign_user_by_email

from . import blueprint


SESSION_NAME_ID = "samlNameId"
SESSION_SESSION_ID = "samlSessionIndex"
SESSION_USERDATA_KEY = "samlUserdata"

logger = logging.getLogger(__name__)


def init_saml_auth(req):
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


class UserDataMapping(enum.Enum):
    username = "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"
    first_name = "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname"
    last_name = "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname"
    email = "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress"


def get_userdata(nameid: str, saml_data: Dict[str, List[str]]) -> UserData:
    userdata = UserData(
        email=nameid,
        first_name=saml_data[UserDataMapping.first_name.value][0],
        last_name=saml_data[UserDataMapping.last_name.value][0],
        user_type="internal",
    )

    if app.config.get("SAML_COMPANY"):
        company = superdesk.get_resource_service("companies").find_one(
            req=None, name=app.config["SAML_COMPANY"]
        )
        if company is not None:
            userdata["company"] = company["_id"]
        else:
            logger.warning("Company %s not found", app.config["SAML_COMPANY"])

    return userdata


@blueprint.route("/api/login/saml", methods=["GET", "POST"])
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
            return redirect(url_for("auth.index", user_error=1))
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
            userdata=get_userdata(
                session[SESSION_NAME_ID], session[SESSION_USERDATA_KEY]
            ),
        )

    return redirect(auth.login())


@blueprint.route("/api/login/saml_metadata")
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
