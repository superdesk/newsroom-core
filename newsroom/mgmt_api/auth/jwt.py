import base64
import hmac
import hashlib
import json

from typing import Any

from superdesk.utc import utcnow
from superdesk.core import get_app_config
from superdesk.core.types import Request
from superdesk import get_resource_service
from superdesk.errors import SuperdeskApiError
from superdesk.core.auth.user_auth import UserAuthProtocol


class JWTTokenAuth(UserAuthProtocol):
    """
    Implements Async JWT authentication by extending UserAuthProtocol.
    """

    @staticmethod
    def _decode_token(token: str) -> dict[str, Any]:
        """
        Decodes a JWT token uses manual base64 decoding.
        """
        try:
            header_b64, payload_b64, signature_b64 = token.split(".")
            payload = json.loads(base64.urlsafe_b64decode(payload_b64 + "==").decode())

            return payload
        except Exception:
            raise SuperdeskApiError.unauthorizedError()

    @staticmethod
    def _verify_signature(token: str, secret: str) -> bool:
        """
        Verifies the JWT signature manually using HMAC-SHA256.
        """
        try:
            header_b64, payload_b64, signature_b64 = token.split(".")
            unsigned_token = f"{header_b64}.{payload_b64}"

            expected_signature = (
                base64.urlsafe_b64encode(hmac.new(secret.encode(), unsigned_token.encode(), hashlib.sha256).digest())
                .decode()
                .strip("=")
            )

            return hmac.compare_digest(expected_signature, signature_b64)
        except Exception:
            return False

    async def authenticate(self, request: Request):
        """
        Extracts the JWT token, verifies it, and starts a session.
        """
        token = request.get_header("Authorization")
        if token:
            token = token.strip()
            if token.lower().startswith(("token", "bearer")):
                token = token.split(" ")[1] if " " in token else ""
        else:
            token = request.storage.session.get("session_token")

        if not token:
            await self.stop_session(request)
            raise SuperdeskApiError.unauthorizedError()

        secret = get_app_config("AUTH_SERVER_SHARED_SECRET")

        if not secret:
            raise SuperdeskApiError.unauthorizedError()

        if not self._verify_signature(token, secret):
            raise SuperdeskApiError.unauthorizedError()

        payload = self._decode_token(token)
        exp = payload.get("exp")

        if exp and utcnow().timestamp() > exp:
            raise SuperdeskApiError.unauthorizedError()

        await self.start_session(request, payload)

    async def start_session(self, request: Request, payload: dict[str, Any]):
        """
        Starts a session and stores the user data.
        """
        user_id = payload.get("client_id")
        user_service = get_resource_service("users")
        user = user_service.find_one(req=None, _id=user_id)

        if not user:
            raise SuperdeskApiError.unauthorizedError()

        request.storage.request.set("auth_token", payload)
        request.storage.request.set("user_id", user_id)
        request.storage.request.set("user", user)

    def get_current_user(self, request: Request) -> dict[str, Any] | None:
        """
        Retrieves the current user from the session.
        """
        return request.storage.request.get("user")
