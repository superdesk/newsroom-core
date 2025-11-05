from superdesk.core.web import EndpointGroup
from superdesk.core.types import Request, BaseModel, Response

from newsroom.news_api.api_tokens.auth import support_auth_token_in_url
from newsroom.news_api.formatters import RSSFormatter

rss_endpoints = EndpointGroup("rss", __name__)


class RSSArgs(BaseModel):
    token: str | None = None


@rss_endpoints.endpoint(
    "rss/<path:token>",
    title="RSS Feed (URL auth)",
    methods=["GET"],
    auth=[support_auth_token_in_url],
)
async def get_rss_token(args: RSSArgs, params: None, request: Request) -> Response:
    return await RSSFormatter().format_feed(args.token, request)


@rss_endpoints.endpoint(
    "rss",
    title="RSS Feed (Header auth)",
    methods=["GET"],
    auth=[support_auth_token_in_url],
)
async def get_rss_authed(args: None, params: RSSArgs, request: Request) -> Response:
    return await RSSFormatter().format_feed(params.token, request)
