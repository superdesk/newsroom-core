from quart_rate_limiter import RateLimiter, rate_limit
from superdesk.flask import request

__all__ = ["rate_limit", "limiter"]


async def get_remote_address():
    # Copied from flask_limiter.util.get_remote_address
    return request.remote_addr or "127.0.0.1"


limiter = RateLimiter(None, key_function=get_remote_address)
