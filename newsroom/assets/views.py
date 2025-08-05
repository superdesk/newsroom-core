from pydantic import BaseModel

from superdesk.core import get_app_config, get_current_async_app
from superdesk.core.types import Response, Request
from superdesk.flask import request as flask_request
from superdesk.storage.superdesk_file import get_file_request_range, generate_response_for_file

from .module import assets_endpoints
from .utils import get_media_file, get_content_disposition


class RouteArguments(BaseModel):
    media_id: str


class UrlParams(BaseModel):
    filename: str | None = None


async def get_upload(media_id: str, filename: str | None = None):
    begin, end = get_file_request_range(flask_request.range if flask_request else None)
    media_file = await get_media_file(media_id, begin=begin, end=end)
    if not media_file:
        return None

    return await generate_response_for_file(
        media_file, content_disposition=get_content_disposition(filename, media_file.content_type)
    )


@assets_endpoints.endpoint("/assets/<path:media_id>", methods=["GET"], auth=False)
async def download_file(args: RouteArguments, params: UrlParams, request: Request) -> Response:
    # Allow access to ``/assets/<media_id>`` if PUBLIC_DASHBOARD is enabled or is a valid session
    if not get_app_config("PUBLIC_DASHBOARD"):
        response = await get_current_async_app().auth.authenticate(request)
        if response:
            return response

    response = await get_upload(args.media_id, params.filename)
    return response if response else await request.abort(404)
