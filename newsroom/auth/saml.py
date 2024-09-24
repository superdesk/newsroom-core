"""SAML Authentication

To enable:
 - add 'newsroom.auth.saml' to INSTALLED_APPS in settings.py
 - add 'python3-saml==1.14.0' to requirements.txt
 - set SAML_PATH in settings.py to path with config and certificates

"""

from typing import Dict, List

import logging
import pathlib
import superdesk

from urllib.parse import urlparse
from quart_babel import gettext
from onelogin.saml2.auth import OneLogin_Saml2_Auth

from superdesk.core import get_app_config
from superdesk.flask import (
    request,
    redirect,
    make_response,
    session,
    url_for,
    render_template,
    abort,
)

from newsroom.flask import flash
from newsroom.types import AuthProviderType, UserData
from newsroom.auth.utils import sign_user_by_email
from .views import blueprint


SESSION_NAME_ID = "samlNameId"
SESSION_SESSION_ID = "samlSessionIndex"
SESSION_USERDATA_KEY = "samlUserdata"
SESSION_SAML_CLIENT = "_saml_client"
SAML_NAME_KEY = "http://schemas.microsoft.com/identity/claims/displayname"

logger = logging.getLogger(__name__)


def init_saml_auth(req):
    saml_client = session.get(SESSION_SAML_CLIENT)
    saml_clients_config = get_app_config("SAML_CLIENTS")

    if saml_clients_config and saml_client and saml_client in saml_clients_config:
        logging.info("Using SAML config for %s", saml_client)
        config_path = pathlib.Path(get_app_config("SAML_BASE_PATH")).joinpath(saml_client)
        if config_path.exists():
            return OneLogin_Saml2_Auth(req, custom_base_path=str(config_path))
        logger.error("SAML config not found in %s", config_path)
    elif saml_client:
        logging.warn("Unknown SAML client %s", saml_client)

    auth = OneLogin_Saml2_Auth(req, custom_base_path=str(get_app_config("SAML_PATH")))
    return auth


async def prepare_flask_request(request):
    url_data = urlparse(request.url)
    return {
        "https": "off" if "http://localhost" in get_app_config("CLIENT_URL", "") else "on",
        "http_host": request.host,
        "server_port": url_data.port,
        "script_name": request.path,
        "get_data": request.args.copy(),
        "post_data": (await request.form).copy(),
    }


def get_userdata(nameid: str, saml_data: Dict[str, List[str]]) -> UserData:
    logger.debug("Attributes for %s = %s", nameid, saml_data)

    userdata = UserData(
        email=nameid,
        user_type="internal",
    )

    for saml_key, user_key in get_app_config("SAML_USER_MAPPING").items():
        if saml_data.get(saml_key):
            userdata[user_key] = saml_data[saml_key][0]  # type: ignore

    if saml_data.get(SAML_NAME_KEY):
        name_list = saml_data[SAML_NAME_KEY][0].split(" ")
        userdata.setdefault("first_name", name_list[0])
        userdata.setdefault(
            "last_name", name_list[-1]
        )  # this might be again first name, but we need something not empty

    # first we try to find company based on email domain
    domain = nameid.split("@")[-1]
    if domain:
        company = superdesk.get_resource_service("companies").find_one(req=None, auth_domains=domain)
        if company is not None:
            userdata["company"] = company["_id"]
            if not company.get("internal"):
                userdata["user_type"] = "public"

    # then based on preconfigured saml client
    if session.get(SESSION_SAML_CLIENT) and not userdata.get("company"):
        company = superdesk.get_resource_service("companies").find_one(
            req=None, auth_domains=session[SESSION_SAML_CLIENT]
        )
        if company is not None:
            userdata["company"] = company["_id"]
            if not company.get("internal"):
                userdata["user_type"] = "public"

    # last option is global env variable
    saml_company_config = get_app_config("SAML_COMPANY")
    if saml_company_config and not userdata.get("company"):
        company = superdesk.get_resource_service("companies").find_one(req=None, name=saml_company_config)
        if company is not None:
            userdata["company"] = company["_id"]
        else:
            logger.warning("Company %s not found", saml_company_config)

    return userdata


@blueprint.route("/login/saml", methods=["GET", "POST"])
async def saml():
    req = await prepare_flask_request(request)
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
            await flash(gettext("There was an error when using SSO"), "danger")
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
        return await sign_user_by_email(
            session[SESSION_NAME_ID],
            auth_type=AuthProviderType.SAML,
            create_missing=True,
            userdata=get_userdata(session[SESSION_NAME_ID], session[SESSION_USERDATA_KEY]),
            validate_login_attempt=True,
        )

    return redirect(auth.login())


@blueprint.route("/login/saml_metadata")
async def saml_metadata():
    req = await prepare_flask_request(request)
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
async def client_login(client):
    if not client or client not in get_app_config("SAML_CLIENTS"):
        return abort(404)
    session[SESSION_SAML_CLIENT] = client
    return await render_template("login_client.html", client=client)
