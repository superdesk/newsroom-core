import logging
from markupsafe import Markup
import requests
from urllib.parse import urlencode

from wtforms import Field, ValidationError
from quart_babel import gettext, lazy_gettext

from superdesk.core import get_app_config, get_current_app
from superdesk.flask import request

__all__ = [
    "RecaptchaField",
    "validate_recaptcha_request",
]

logger = logging.getLogger(__name__)
session = requests.Session()

# The code from this file was copied from flask_wtf.recaptch
# because quart_wtf doesn't support recaptcha
# see: https://github.com/wtforms/flask-wtf/tree/main/src/flask_wtf/recaptcha

RECAPTCHA_SCRIPT_DEFAULT = "https://www.google.com/recaptcha/api.js"
RECAPTCHA_DIV_CLASS_DEFAULT = "g-recaptcha"
RECAPTCHA_TEMPLATE = """
<script src='%s' async defer></script>
<div class="%s" %s></div>
"""

RECAPTCHA_VERIFY_SERVER_DEFAULT = "https://www.google.com/recaptcha/api/siteverify"
RECAPTCHA_ERROR_CODES = {
    "missing-input-secret": lazy_gettext("The secret parameter is missing."),
    "invalid-input-secret": lazy_gettext("The secret parameter is invalid or malformed."),
    "missing-input-response": lazy_gettext("The response parameter is missing."),
    "invalid-input-response": lazy_gettext("The response parameter is invalid or malformed."),
}


class RecaptchaWidget:
    def __call__(self, field: Field, error=None, **kwargs):
        """Returns the recaptcha input HTML"""

        public_key = get_app_config("RECAPTCHA_PUBLIC_KEY")
        if not public_key:
            raise RuntimeError("RECAPTCHA_PUBLIC_KEY config not set")

        html = get_app_config("RECAPTCHA_HTML")
        if html:
            return Markup(html)

        params = get_app_config("RECAPTCHA_PARAMETERS")
        script = get_app_config("RECAPTCHA_SCRIPT")
        if not script:
            script = RECAPTCHA_SCRIPT_DEFAULT
        if params:
            script += "?" + urlencode(params)
        attrs = get_app_config("RECAPTCHA_DATA_ATTRS", {})
        attrs["sitekey"] = public_key
        snippet = " ".join(f'data-{k}="{attrs[k]}"' for k in attrs)  # noqa: B028, B907
        div_class = get_app_config("RECAPTCHA_DIV_CLASS")
        if not div_class:
            div_class = RECAPTCHA_DIV_CLASS_DEFAULT
        return Markup(RECAPTCHA_TEMPLATE % (script, div_class, snippet))


class RecaptchaField(Field):
    widget = RecaptchaWidget()


async def validate_recaptcha_request() -> None:
    try:
        if get_current_app().testing:
            return

        if request.is_json:
            response = (await request.get_json()).get("g-recaptcha-response", "")
        else:
            response = (await request.form).get("g-recaptcha-response", "")
        remote_ip = request.remote_addr

        if not response:
            raise ValidationError(gettext("The response parameter is missing."))

        if not _validate_recaptcha(response, remote_ip):
            raise ValidationError(gettext("Failed to validate recaptcha."))
    except Exception as error:
        logger.exception(error)
        raise ValidationError(gettext("Unknown error while validating request."))


def _validate_recaptcha(response: str, remote_ip: str) -> bool:
    """Performs the actual validation."""

    private_key = get_app_config("RECAPTCHA_PRIVATE_KEY")
    if not private_key:
        raise RuntimeError("No RECAPTCHA_PRIVATE_KEY config set")

    verify_server = get_app_config("RECAPTCHA_VERIFY_SERVER") or RECAPTCHA_VERIFY_SERVER_DEFAULT
    data = urlencode({"secret": private_key, "remoteip": remote_ip, "response": response})

    http_response = session.get(f"{verify_server}?{data}")

    if http_response.status_code != 200:
        return False

    json_resp = http_response.json()

    if json_resp["success"]:
        return True

    for error in json_resp.get("error-codes", []):
        if error in RECAPTCHA_ERROR_CODES:
            raise ValidationError(RECAPTCHA_ERROR_CODES[error])

    return False
