from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from os import path
from io import BytesIO

from werkzeug.utils import secure_filename

from superdesk.core import get_app_config, get_current_app
from superdesk.core.web import Response, Request
from superdesk.media.media_operations import guess_media_extension

from .module import assets_endpoints
from .utils import get_media_file, CACHE_MAX_AGE

from newsroom.decorator import is_valid_session, clear_session_and_redirect_to_login


class RouteArguments(BaseModel):
    media_id: str


class UrlParams(BaseModel):
    filename: str | None = None


@assets_endpoints.endpoint("/assets/<string:media_id>", methods=["GET"])
async def get_upload(args: RouteArguments, params: UrlParams, request: Request) -> Response:
    if not get_app_config("PUBLIC_DASHBOARD") and not is_valid_session():
        return clear_session_and_redirect_to_login()

    # TODO-ASYNC: Create new FileResponse type in superdesk-core, and use that where file downloads are requested
    media_file = await get_media_file(args.media_id)
    if not media_file:
        return await request.abort(404)

    content = await media_file.read()

    app = get_current_app()
    file_body = app.as_any().response_class.io_body_class(BytesIO(content))
    response = app.response_class(file_body, mimetype=media_file.content_type)
    response.content_length = media_file.length
    response.last_modified = media_file.upload_date
    response.set_etag(media_file.md5)
    response.cache_control.max_age = CACHE_MAX_AGE
    response.cache_control.s_max_age = CACHE_MAX_AGE
    response.cache_control.public = True
    response.expires = datetime.now(timezone.utc) + timedelta(seconds=CACHE_MAX_AGE)

    # Add ``accept_ranges`` & ``complete_length`` so video seeking is supported
    await response.make_conditional(request, accept_ranges=True, complete_length=media_file.length)

    if params.filename:
        _filename, ext = path.splitext(params.filename)
        if not ext:
            ext = guess_media_extension(media_file.content_type)
        filename = secure_filename(f"{_filename}{ext}")
        response.headers["Content-Type"] = media_file.content_type
        response.headers["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)
    else:
        response.headers["Content-Disposition"] = "inline"

    return response
