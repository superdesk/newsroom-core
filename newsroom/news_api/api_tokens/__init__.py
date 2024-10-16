import ipaddress
from datetime import timedelta

from quart_babel import gettext
from eve.auth import TokenAuth

from superdesk.core import get_current_app, get_app_config
from superdesk.flask import Blueprint, g, abort, request
import superdesk
from superdesk.utc import utcnow
from superdesk import get_resource_service

from newsroom.types import CompanyResource
from newsroom.companies import CompanyServiceAsync
from .resource import NewsApiTokensResource
from .service import NewsApiTokensService


API_TOKENS = "news_api_tokens"

blueprint = Blueprint("news_api_tokens", __name__)

from . import views  # noqa


class CompanyTokenAuth(TokenAuth):
    def check_auth(self, token_id, allowed_roles, resource, method):
        """Try to find auth token and if valid put subscriber id into ``g.company_id``."""
        app = get_current_app()
        token = app.data.mongo.find_one(API_TOKENS, req=None, _id=token_id)
        if not token:
            return False
        # Check if the token has expired
        now = utcnow()
        if token.get("expiry") and token.get("expiry") < now:
            return False
        # Make sure the API is enabled
        if not token.get("enabled", False):
            return False

        # Make sure that the company is enabled
        company = app.data.mongo.find_one("companies", req=None, _id=token.get("company"))
        if not company:
            return False
        if not company.get("is_enabled", False):
            return False

        valid_network = False
        if company.get("allowed_ip_list"):
            # Request.access_route: If a forwarded header exists this is a
            # list of all ip addresses from the client ip to the last proxy server.
            # Ref. https://tedboy.github.io/flask/generated/generated/werkzeug.Request.access_route.html
            access_route = request.access_route[0] if request.access_route[0] != "<local>" else "127.0.0.1"
            request_ip_address = ipaddress.ip_address(access_route)
            for i in company["allowed_ip_list"]:
                if request_ip_address in ipaddress.ip_network(i, strict=False):
                    valid_network = True

            if not valid_network:
                return False

        # Check rate_limit
        updates = {}
        new_period = False
        rate_limit_requests = get_app_config("RATE_LIMIT_REQUESTS")
        if rate_limit_requests:
            new_period = not token.get("rate_limit_expiry") or token["rate_limit_expiry"] <= now
            if new_period:
                updates["rate_limit_requests"] = 1
            elif token.get("rate_limit_expiry"):
                if token.get("rate_limit_requests", 0) >= rate_limit_requests:
                    abort(429, gettext("Rate limit exceeded"))
                else:
                    updates["rate_limit_requests"] = token.get("rate_limit_requests", 0) + 1

        rate_limit_period = get_app_config("RATE_LIMIT_PERIOD")
        if rate_limit_period and new_period:
            updates["rate_limit_expiry"] = now + timedelta(seconds=rate_limit_period)

        if updates:
            get_resource_service(API_TOKENS).patch(token_id, updates)

            # Set Flask global variables
            g.rate_limit_requests = updates["rate_limit_requests"]
            if updates.get("rate_limit_expiry"):
                g.rate_limit_expiry = updates["rate_limit_expiry"]

        company_id = token.get("company")
        g.company_id = str(company_id)

        # TODO-ASYNC: Improve auth for NewsAPI, when there is no User associated with a request
        # Store CompanyResource instance on request cache (to be used with get_company_from_request)
        company_dict = CompanyServiceAsync().mongo.find_one({"_id": company_id})
        if company_dict:
            g.company_instance = CompanyResource.from_dict(company_dict)

        return g.company_id


def init_app(app):
    if get_app_config("NEWS_API_ENABLED"):
        superdesk.register_resource(API_TOKENS, NewsApiTokensResource, NewsApiTokensService, _app=app)
