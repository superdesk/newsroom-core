from pydantic import BaseModel

from superdesk.core.web import EndpointGroup
from superdesk.core.types import Request
from newsroom.history_async import HistoryService

from newsroom.assets import get_upload
from newsroom.news_api.utils import post_api_audit
from newsroom.news_api.api_tokens.auth import support_auth_token_in_url

assets_endpoints = EndpointGroup("assets", __name__)


class RouteParams(BaseModel):
    token: str | None = None


class RouteArguments(BaseModel):
    asset_id: str
    item_id: str | None = None
    token: str | None = None


@assets_endpoints.endpoint("assets/<path:asset_id>/<item_id>", methods=["GET"], auth=[support_auth_token_in_url])
async def download(args: RouteArguments, params: RouteParams, request: Request):
    """
    Called on download of a media item, keeps a record of the download
    """

    response = await return_item(args, None, request=request)
    await HistoryService().log_api_media_download(args.item_id, args.asset_id)
    return response


@assets_endpoints.endpoint("assets/<string:asset_id>", methods=["GET"], auth=[support_auth_token_in_url])
async def get_item(args: RouteArguments, params: RouteParams, request: Request):
    """
    Get media item via the assets endpoint
    @param args:
    @param params:
    @param request:
    @return:
    """

    return await return_item(args, None, request)


async def return_item(args: RouteArguments, _p: None, request: Request):
    """
    Get media item via the asset id and record the download
    @param args:
    @param _p:
    @param request:
    @return:
    """

    await post_api_audit(request, [args.asset_id])

    response = await get_upload(args.asset_id)
    if not response:
        await request.abort(404)
    return response
