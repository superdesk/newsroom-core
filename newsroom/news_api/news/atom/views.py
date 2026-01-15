from superdesk.core.web import EndpointGroup
from superdesk.core.types import Request, BaseModel, Response

from newsroom.news_api.api_tokens.auth import support_auth_token_in_url, support_auth_basic_auth
from newsroom.news_api.formatters import AtomFormatter

atom_endpoints = EndpointGroup("atom", __name__)


class AtomArgs(BaseModel):
    token: str | None = None


@atom_endpoints.endpoint(
    "atom/<path:token>",
    title="ATOM Feed (URL auth)",
    methods=["GET"],
    auth=[support_auth_token_in_url],
)
async def get_atom_token(args: AtomArgs, params: None, request: Request) -> Response:
    return await AtomFormatter().format_feed(args.token, request)


@atom_endpoints.endpoint(
    "atom",
    title="ATOM Feed (Header auth)",
    methods=["GET"],
    auth=[support_auth_basic_auth, support_auth_token_in_url],
)
async def get_atom_authed(args: None, params: AtomArgs, request: Request) -> Response:
    return await AtomFormatter().format_feed(params.token, request)
