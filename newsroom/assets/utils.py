import os
import bson

from werkzeug.utils import secure_filename
from typing import Any

from newsroom.core import get_current_wsgi_app
from superdesk.core.types import SuperdeskAsyncFile
from superdesk.flask import url_for
from superdesk.upload import upload_url as _upload_url
from superdesk.media.media_operations import guess_media_extension

from .module import ASSETS_ENDPOINT_GROUP_NAME, ASSETS_RESOURCE

CACHE_MAX_AGE = 3600 * 24 * 7  # 7 days


async def get_media_file(media_id: str, begin: int = 0, end: int | None = None) -> SuperdeskAsyncFile | None:
    """
    Asynchronously retrieves a media file from the database using its media ID.

    Returns:
        The media file object if found, otherwise None.
    """
    app = get_current_wsgi_app()
    try:
        result = await app.media.get_async(media_id, ASSETS_RESOURCE, begin=begin, end=end)
        return result
    except bson.errors.InvalidId:
        return None


def get_content_disposition(filename: str | None, content_type: str = "") -> str:
    """
    Generates the Content-Disposition header value based on the filename and metadata.

    Returns:
        str: A Content-Disposition header string.
    """
    if filename:
        _filename, ext = os.path.splitext(filename)
        if not ext:
            ext = guess_media_extension(content_type)
        filename = secure_filename(f"{_filename}{ext}")
        return f'attachment; filename="{filename}"'

    return "inline"


async def save_file_and_get_url(file: Any) -> str:
    """
    Asynchronously uploads a file to the media storage service and generates a URL
    for accessing the uploaded file.

    Args:
        file: The file to be uploaded.

    Returns:
        str: A URL to the uploaded file if a file is found and successfully uploaded; otherwise, None.
        None is returned if no file is found for the provided key or if the file fails to upload.
    """
    app = get_current_wsgi_app()
    filename = secure_filename(file.filename)

    await app.media.put_async(file, filename, resource=ASSETS_RESOURCE, _id=filename, content_type=file.content_type)

    endpoint = f"{ASSETS_ENDPOINT_GROUP_NAME}.download_file"
    return url_for(endpoint, media_id=filename)


def upload_url(media_id: str):
    return _upload_url(media_id, view="assets.get_media_streamed")
