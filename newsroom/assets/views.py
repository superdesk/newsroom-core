from pydantic import BaseModel

from superdesk.upload import upload_url as _upload_url
from superdesk.core.web import Response, Request

from .module import assets_endpoints
from .utils import generate_response_headers, get_media_file

# from newsroom.decorator import is_valid_session, clear_session_and_redirect_to_login


class RouteArguments(BaseModel):
    media_id: str


@assets_endpoints.endpoint("/assets/<string:media_id>", methods=["GET"])
async def get_upload(args: RouteArguments, _p, request: Request) -> Response:
    # if not get_app_config("PUBLIC_DASHBOARD") and not is_valid_session():
    #     return clear_session_and_redirect_to_login()

    media_file = await get_media_file(args.media_id)
    if not media_file:
        return await request.abort(404)

    content = await media_file.read()
    return Response(content, 200, generate_response_headers(media_file))


def upload_url(media_id):
    return _upload_url(media_id, view="assets.get_media_streamed")
