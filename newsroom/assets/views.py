from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from os import path
from io import BytesIO

from werkzeug.utils import secure_filename

from superdesk.core import get_app_config, get_current_app, get_current_async_app
from superdesk.core.types import Response, Request
from superdesk.flask import request as flask_request
from superdesk.media.media_operations import guess_media_extension

from .module import assets_endpoints
from .utils import get_media_file, CACHE_MAX_AGE


class RouteArguments(BaseModel):
    media_id: str


class UrlParams(BaseModel):
    filename: str | None = None


async def get_upload(media_id: str, filename: str | None = None):
    media_file = await get_media_file(media_id)
    if not media_file:
        return None

    content = await media_file.read()

    app = get_current_app()
    metadata = media_file.metadata or {}
    mimetype = metadata.get("contentType", media_file.content_type)
    file_body = app.as_any().response_class.io_body_class(BytesIO(content))
    response = app.response_class(file_body, mimetype=mimetype)
    response.content_length = media_file.length
    response.last_modified = media_file.upload_date

    # TODO-ASYNC: Set etag from ``media_file`` (as `md5` attribute is not defined in newer PyMongo)
    if getattr(media_file, "md5", None):
        response.set_etag(media_file.md5)

    response.cache_control.max_age = CACHE_MAX_AGE
    response.cache_control.s_max_age = CACHE_MAX_AGE
    response.cache_control.public = True
    response.expires = datetime.now(timezone.utc) + timedelta(seconds=CACHE_MAX_AGE)

    # Add ``accept_ranges`` & ``complete_length`` so video seeking is supported
    await response.make_conditional(flask_request, accept_ranges=True, complete_length=media_file.length)

    if filename:
        _filename, ext = path.splitext(filename)
        if not ext:
            ext = guess_media_extension(mimetype)
        filename = secure_filename(f"{_filename}{ext}")
        response.headers["Content-Type"] = mimetype
        response.headers["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)
    else:
        response.headers["Content-Disposition"] = "inline"

    return response


@assets_endpoints.endpoint("/assets/<string:media_id>", methods=["GET"], auth=False)
async def download_file(args: RouteArguments, params: UrlParams, request: Request) -> Response:
    if not get_app_config("PUBLIC_DASHBOARD"):
        response = await get_current_async_app().auth.authenticate(request)
        if response:
            return response

    response = await get_upload(args.media_id, params.filename)
    return response if response else await request.abort(404)
