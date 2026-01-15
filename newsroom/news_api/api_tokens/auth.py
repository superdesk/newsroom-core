import ipaddress
import base64
from typing import Any
from datetime import timedelta
from quart_babel import gettext

from superdesk.utc import utcnow
from superdesk.core.types import Request
from superdesk.core.app import UserAuthProtocol
from superdesk.flask import request as flask_request
from superdesk import get_resource_service, get_app_config

from newsroom.exceptions import AuthorizationError
from newsroom.companies.companies_async import CompanyService
from newsroom.news_api.utils import get_company_from_newsapi_request

API_TOKENS = "news_api_tokens"


async def company_required_auth_rule(request: Request) -> None:
    # AuthorizationError(403) error is raised in the following util
    # so we use that for the auth rule
    get_company_from_newsapi_request(request)
    return None


async def valid_IP_if_required_rule(request: Request) -> None:
    company = request.storage.request.get("company_instance")

    valid_network = False
    if company.allowed_ip_list:
        # Request.access_route: If a forwarded header exists this is a
        # list of all ip addresses from the client ip to the last proxy server.
        # Ref. https://tedboy.github.io/flask/generated/generated/werkzeug.Request.access_route.html
        access_route = flask_request.access_route[0] if flask_request.access_route[0] != "<local>" else "127.0.0.1"
        request_ip_address = ipaddress.ip_address(access_route)
        for i in company.allowed_ip_list:
            if request_ip_address in ipaddress.ip_network(i, strict=False):
                valid_network = True

        if not valid_network:
            raise AuthorizationError(401, gettext("IP Address not allowed."))

    return None


async def support_auth_token_in_url(request: Request) -> None:
    """Flag to indicate this endpoint supports using the ``token`` in the URL"""
    return None


async def support_auth_basic_auth(request: Request) -> None:
    """Flag to indicate this endpoint supports using the basic auth"""
    return None


class CompanyTokenAuth(UserAuthProtocol):
    def get_token_from_request(self, request: Request) -> str | None:
        """
        Extracts the token from `Authorization` header. Code taken partly
        from eve.Auth module
        """
        supports_basic_auth = (
            isinstance(request.endpoint.auth, list) and support_auth_basic_auth in request.endpoint.auth
        ) or (isinstance(request.endpoint.auth, dict) and support_auth_basic_auth in request.endpoint.auth.values())
        supports_token_in_url = (
            isinstance(request.endpoint.auth, list) and support_auth_token_in_url in request.endpoint.auth
        ) or (isinstance(request.endpoint.auth, dict) and support_auth_token_in_url in request.endpoint.auth.values())

        auth = (request.get_header("Authorization") or "").strip()
        if len(auth):
            if auth.lower().startswith(("token", "bearer")):
                return auth.split(" ")[1] if " " in auth else None

            if supports_basic_auth and auth.lower().startswith("basic"):
                base64_payload = auth.split(" ", 1)[1]

                credentials_bytes = base64.b64decode(base64_payload)
                credentials = credentials_bytes.decode("utf-8")
                username, password = credentials.split(":", 1)

                return username if username else password

            # In case just the token was passed
            return auth

        if supports_token_in_url:
            token = request.get_url_arg("token") or request.get_view_args("token")
            if token:
                return token

        return None

    def get_default_auth_rules(self):
        return [company_required_auth_rule, valid_IP_if_required_rule]

    async def authenticate(self, request: Request) -> None:
        """
        Tries to find the auth token in the request and if valid puts subscriber id into ``g.company_id``.
        """
        tokens_service = get_resource_service(API_TOKENS)
        token_missing_exception = AuthorizationError(
            401, gettext("Authorization token missing."), title=gettext("401. Forbidden")
        )
        token_id = self.get_token_from_request(request)
        if token_id is None:
            raise token_missing_exception

        # TODO-ASYNC: replace when api_tokens are async
        token = tokens_service.find_one(req=None, _id=token_id)
        if token is None:
            raise token_missing_exception

        await self.check_token_validity(request, token)
        await self.start_session(request, token)
        await self.check_rate_limit(request, token)

    async def start_session(self, request: Request, token: dict[str, Any]):
        company = await CompanyService().find_by_id(token.get("company"))

        # TODO-ASYNC: replace token with actual token resource model once api_tokens is async
        request.storage.request.set("company_auth_token", token)
        request.storage.request.set("company_instance", company)
        request.storage.request.set("company_id", str(company.id))

    async def check_token_validity(self, request: Request, token: dict[str, Any]):
        """
        Check if the token is not expired or if it is not enabled, otherwise
        it throws an AuthorizationError
        """
        now = utcnow()
        if token.get("expiry") and token.get("expiry") < now:
            raise AuthorizationError(403, gettext("Token expired."), title=gettext("403. Forbidden"))

        if not token.get("enabled", False):
            raise AuthorizationError(
                403,
                gettext("The requested resource is not available for your subscription."),
                title=gettext("403. Forbidden"),
            )

    async def check_rate_limit(self, request: Request, token: dict[str, Any]):
        updates = {}
        now = utcnow()
        new_period = False
        rate_limit_requests = get_app_config("RATE_LIMIT_REQUESTS")
        tokens_service = get_resource_service(API_TOKENS)

        if rate_limit_requests:
            new_period = not token.get("rate_limit_expiry") or token["rate_limit_expiry"] <= now
            if new_period:
                updates["rate_limit_requests"] = 1
            elif token.get("rate_limit_expiry"):
                if token.get("rate_limit_requests", 0) >= rate_limit_requests:
                    await request.abort(429, gettext("Rate limit exceeded"))
                else:
                    updates["rate_limit_requests"] = token.get("rate_limit_requests", 0) + 1

        rate_limit_period = get_app_config("RATE_LIMIT_PERIOD")
        if rate_limit_period and new_period:
            updates["rate_limit_expiry"] = now + timedelta(seconds=rate_limit_period)

        if updates:
            tokens_service.patch(token.get("token"), updates)
            storage = request.storage.request

            storage.set("rate_limit_requests", updates["rate_limit_requests"])
            if updates.get("rate_limit_expiry"):
                storage.set("rate_limit_expiry", updates["rate_limit_expiry"])

    def get_current_user(self, _r: Request):
        return None
