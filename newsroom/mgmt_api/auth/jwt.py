import logging
import time
from typing import List, Optional

from authlib.jose import jwt
from authlib.jose.errors import BadSignatureError, ExpiredTokenError, DecodeError

from newsroom.auth.utils import get_current_request

from superdesk.core import get_app_config
from superdesk.core.types import Request
from superdesk.core.auth.token_auth import TokenAuthorization
from superdesk.errors import SuperdeskApiError
from superdesk.core.auth.rules import endpoint_intrinsic_auth_rule

logger = logging.getLogger(__name__)


class JWTTokenAuth(TokenAuthorization):
    """
    Implements Async JWT authentication by extending the new async TokenAuthorization.
    """

    def get_default_auth_rules(self) -> List:
        """
        Returns the default authentication rules.

        :return: A list of authentication rules.
        """
        return [endpoint_intrinsic_auth_rule]

    def get_token_from_request(self, request: Request) -> Optional[str]:
        """
        Extracts the token from the `Authorization` header.

        :param request: The request object containing headers.
        :return: The extracted token or None if not found.
        """
        auth = (request.get_header("Authorization") or "").strip()
        if auth.lower().startswith(("token", "bearer", "basic")):
            return auth.split(" ")[1] if " " in auth else None
        return auth or None

    def check_auth(self, request: Optional[Request] = None) -> dict:
        """
        Validates the JWT token and returns the decoded payload.

        :param request: The request object. Defaults to the current request if not provided.
        :return: The decoded JWT payload as a dictionary.
        :raises SuperdeskApiError: If the token is missing, invalid, or expired.
        """
        request = request or get_current_request()
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
            decoded_jwt.validate_exp(now=int(time.time()), leeway=0)
            return decoded_jwt
        except (BadSignatureError, ExpiredTokenError, DecodeError) as e:
            logger.error(f"JWT authentication failed: {e}")
            raise SuperdeskApiError.unauthorizedError()

    async def authenticate(self, request: Optional[Request] = None) -> None:
        """
        Asynchronously authenticates the request by validating the JWT token.

        :param request: The request object. Defaults to the current request if not provided.
        :raises SuperdeskApiError: If authentication fails.
        """
        decoded_jwt = self.check_auth(request)
        self.start_session(request, decoded_jwt)

    def start_session(self, request: Request, token_data: dict) -> None:
        """
        Starts a session by storing token data in the request storage.

        :param request: The request object.
        :param token_data: The decoded JWT payload.
        """
        request.storage.request.set("auth_token", token_data)
        request.storage.request.set("user_id", token_data.get("client_id"))

    def get_current_user(self, request: Request) -> Optional[str]:
        """
        Retrieves the current user ID from the session.

        :param request: The request object.
        :return: The user ID if available, otherwise None.
        """
        return request.storage.request.get("user_id")

    def authorized(self, allowed_roles: List[str], resource: str, method: str) -> bool:
        """
        Checks if the request is authorized by validating the token.

        :param allowed_roles: A list of roles allowed to access the resource.
        :param resource: The resource being accessed.
        :param method: The HTTP method of the request.
        :return: True if authorized, False otherwise.
        """
        request = get_current_request()
        token = self.get_token_from_request(request)

        if not token:
            logger.warning("No token found in request")
            raise SuperdeskApiError.unauthorizedError()

        try:
            self.check_auth(request)
            return True
        except SuperdeskApiError:
            return False  # Return False instead of raising an error
