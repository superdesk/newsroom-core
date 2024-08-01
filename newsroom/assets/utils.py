import os
import bson

from werkzeug.utils import secure_filename
from motor.motor_asyncio import AsyncIOMotorGridOut
from typing import Any, Mapping, Optional, Sequence, cast

from superdesk.core import get_current_app
from superdesk.flask import request, url_for
from superdesk.upload import upload_url as _upload_url
from superdesk.media.media_operations import guess_media_extension

from .module import ASSETS_RESOURCE

CACHE_MAX_AGE = 3600 * 24 * 7  # 7 days


async def get_media_file(media_id):
    from newsroom.web.factory import NewsroomWebApp

    app = cast(NewsroomWebApp, get_current_app())

    try:
        result = await app.media_async.get(media_id, ASSETS_RESOURCE)
        return result
    except bson.errors.InvalidId:
        return None


def get_content_disposition(filename: Optional[str], metadata: Mapping[str, Any] = {}) -> str:
    if filename:
        _filename, ext = os.path.splitext(filename)
        if not ext:
            ext = guess_media_extension(metadata.get("contentType"))
        filename = secure_filename(f"{_filename}{ext}")
        return f'attachment; filename="{filename}"'

    return "inline"


def generate_response_headers(media_file: AsyncIOMotorGridOut) -> Sequence:
    metadata = media_file.metadata or {}

    return [
        ("Content-Disposition", get_content_disposition(media_file.filename, metadata)),
        ("Last-Modified", media_file.upload_date),
        ("Cache-Control", f"max-age={CACHE_MAX_AGE}, public"),
        ("Content-Type", metadata.get("contentType", media_file.content_type))
        # TODO:
        # - set etag which not sure if it's required
        # - find alternative to response.make_conditional(request, accept_ranges=True, complete_length=media_file.length)
    ]


def get_file(key):
    file = request.files.get(key)
    if file:
        filename = secure_filename(file.filename)
        get_current_app().media.put(file, resource=ASSETS_RESOURCE, _id=filename, content_type=file.content_type)
        return url_for("upload.get_upload", media_id=filename)


def upload_url(media_id: str):
    return _upload_url(media_id, view="assets.get_media_streamed")
