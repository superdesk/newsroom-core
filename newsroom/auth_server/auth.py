from time import time
from authlib.jose import jwt
from authlib.jose.errors import BadSignatureError, ExpiredTokenError, DecodeError
from eve.auth import TokenAuth
import logging

from superdesk.core import get_app_config

logger = logging.getLogger(__name__)


class JWTAuth(TokenAuth):
    """
    Implements JWT auth logic.
    """

    def check_auth(self, token, allowed_roles, resource, method):
        """
        This function is called to check if a token is valid. Must be
        overridden with custom logic.
        :param token: token.
        :param allowed_roles: allowed user roles.
        :param resource: resource being requested.
        :param method: HTTP method being executed (POST, GET, etc.)
        """
        if not get_app_config("AUTH_SERVER_SHARED_SECRET"):
            logger.warning("AUTH_SERVER_SHARED_SECRET is not configured in default settings")
            return False

        # decode jwt
        try:
            decoded_jwt = jwt.decode(s=token, key=get_app_config("AUTH_SERVER_SHARED_SECRET"))
            decoded_jwt.validate_exp(now=time(), leeway=0)
        except (BadSignatureError, ExpiredTokenError, DecodeError):
            return False

        return True
