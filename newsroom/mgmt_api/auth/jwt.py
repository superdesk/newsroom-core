from superdesk.core.auth.token_auth import TokenAuthorization
from superdesk.core.types import Request
from superdesk.errors import SuperdeskApiError
from authlib.jose import jwt
from authlib.jose.errors import BadSignatureError, ExpiredTokenError, DecodeError
from superdesk.core import get_app_config
from time import time
import logging
from newsroom.auth.utils import get_current_request

logger = logging.getLogger(__name__)


class JWTTokenAuth(TokenAuthorization):
    """
    Implements Async JWT authentication by extending the new async TokenAuthorization.
    """

    def get_token_from_request(self, request: Request) -> str | None:
        """
        Extracts the token from `Authorization` header.
        """
        auth = (request.get_header("Authorization") or "").strip()
        if auth.lower().startswith(("token", "bearer", "basic")):
            return auth.split(" ")[1] if " " in auth else None
        return auth if auth else None

    def authenticate(self, request: Request = None):
        """
        Validates the JWT token and authenticates the user.
        """
        if request is None:
            request = get_current_request()
        token = self.get_token_from_request(request)
        if not token:
            logger.warning("Missing Authorization token")
            raise SuperdeskApiError.unauthorizedError()

        secret = get_app_config("AUTH_SERVER_SHARED_SECRET")
        if not secret:
            logger.warning("AUTH_SERVER_SHARED_SECRET is not configured in default settings")
            raise SuperdeskApiError.unauthorizedError()

        try:
            decoded_jwt = jwt.decode(token, key=secret)
            decoded_jwt.validate_exp(now=int(time()), leeway=0)
        except (BadSignatureError, ExpiredTokenError, DecodeError) as e:
            logger.error(f"JWT authentication failed: {e}")
            raise SuperdeskApiError.unauthorizedError()

        self.start_session(request, decoded_jwt)

    def start_session(self, request: Request, token_data: dict):
        """
        Starts a session by storing token data.
        """
        request.storage.request.set("auth_token", token_data)
        request.storage.request.set("user_id", token_data.get("client_id"))

    def get_current_user(self, request: Request):
        """
        Retrieves the current user from the session.
        """
        return request.storage.request.get("user_id")

    def authorized(self, allowed_roles, resource, method) -> bool:
        """
        Checks if the request is authorized by validating the token.
        """
        request = get_current_request()
        token = self.get_token_from_request(request)
        if not token:
            logger.warning("No token found in request")
            return False

        try:
            self.authenticate(request)
            return True
        except SuperdeskApiError:
            return False  # Return False instead of raising an error
