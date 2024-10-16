from typing import Callable

from quart import Blueprint
from quart_rate_limiter import RateLimiter as BaseRateLimiter, rate_limit, RateLimit

from superdesk.core import get_current_app
from superdesk.flask import request

__all__ = ["rate_limit", "limiter"]


async def get_remote_address():
    # Copied from flask_limiter.util.get_remote_address
    return request.remote_addr or "127.0.0.1"


class RateLimiter(BaseRateLimiter):
    def _get_limits_for_view_function(self, view_func: Callable, blueprint: Blueprint | None) -> list[RateLimit]:
        try:
            # Make RateLimiter work with Endpoint/EndpointGroups
            endpoint = get_current_app().get_endpoint_for_current_request()
            if endpoint:
                return super()._get_limits_for_view_function(endpoint.func, blueprint)
        except (RuntimeError, AttributeError, KeyError):
            pass

        return super()._get_limits_for_view_function(view_func, blueprint)


limiter = RateLimiter(None, key_function=get_remote_address)
