import asyncio
import os
import bson

from werkzeug.utils import secure_filename
from motor.motor_asyncio import AsyncIOMotorGridOut
from typing import Any, Mapping, Optional, Sequence, cast

from superdesk.core import get_current_app
from superdesk.flask import request, url_for
from superdesk.upload import upload_url as _upload_url
from superdesk.media.media_operations import guess_media_extension

from .module import ASSETS_ENDPOINT_GROUP_NAME, ASSETS_RESOURCE

CACHE_MAX_AGE = 3600 * 24 * 7  # 7 days


def get_newsroom_app():
    from newsroom.web.factory import NewsroomWebApp

    return cast(NewsroomWebApp, get_current_app())


async def get_media_file(media_id: str):
    """
    Asynchronously retrieves a media file from the database using its media ID.

    Returns:
        The media file object if found, otherwise None.
    """
    app = get_newsroom_app()
    try:
        result = await app.media_async.get(media_id, ASSETS_RESOURCE)
        return result
    except bson.errors.InvalidId:
        return None


def get_content_disposition(filename: Optional[str], metadata: Mapping[str, Any] = {}) -> str:
    """
    Generates the Content-Disposition header value based on the filename and metadata.

    Returns:
        str: A Content-Disposition header string.
    """
    if filename:
        _filename, ext = os.path.splitext(filename)
        if not ext:
            ext = guess_media_extension(metadata.get("contentType"))
        filename = secure_filename(f"{_filename}{ext}")
        return f'attachment; filename="{filename}"'

    return "inline"


def generate_response_headers(media_file: AsyncIOMotorGridOut) -> Sequence:
    """
    Generates a sequence of HTTP headers for a media file based on its properties.

    Args:
        media_file (AsyncIOMotorGridOut): The media file object retrieved from a database.

    Returns:
        Sequence[Tuple[str, Any]]: A list of tuples representing HTTP response headers
    """
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


async def save_file_and_get_url(file: Any) -> Optional[str]:
    """
    Asynchronously uploads a file to the media storage service and generates a URL
    for accessing the uploaded file.

    Args:
        file: The file to be uploaded.

    Returns:
        Optional[str]: A URL to the uploaded file if a file is found and successfully uploaded; otherwise, None.
        None is returned if no file is found for the provided key or if the file fails to upload.
    """
    app = get_newsroom_app()
    filename = secure_filename(file.filename)

    await app.media_async.put(file, filename, resource=ASSETS_RESOURCE, _id=filename, content_type=file.content_type)

    endpoint = f"{ASSETS_ENDPOINT_GROUP_NAME}.get_upload"
    return url_for(endpoint, media_id=filename)


def upload_url(media_id: str):
    return _upload_url(media_id, view="assets.get_media_streamed")
