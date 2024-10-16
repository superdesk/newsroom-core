from pydantic import BaseModel
from quart_babel import gettext

from newsroom.core import get_current_wsgi_app
from superdesk.core.web import EndpointGroup
from superdesk.core.types import Request

from newsroom.assets import get_upload
from newsroom.news_api.utils import post_api_audit

assets_endpoints = EndpointGroup("assets", __name__)


class RouteArguments(BaseModel):
    asset_id: str


@assets_endpoints.endpoint("assets/<string:asset_id>", methods=["GET"], auth=False)
async def get_item(args: RouteArguments, _p: None, request: Request):
    app = get_current_wsgi_app()
    auth = app.auth

    if not auth.authorized([], None, request.method):
        await request.abort(401, gettext("Invalid token"))

    # TODO-ASYNC: revisit once post_audit is async
    post_api_audit({"_items": [{"_id": args.asset_id}]})

    response = await get_upload(args.asset_id)
    if not response:
        await request.abort(404)
    return response
