import os
import newsroom
import bson.errors

from pydantic import BaseModel
from werkzeug.utils import secure_filename
from motor.motor_asyncio import AsyncIOMotorGridOut
from typing import Any, Mapping, Optional, Sequence, cast

from superdesk.core.module import Module
from superdesk.core import get_current_app
from superdesk.flask import request, url_for
from superdesk.upload import upload_url as _upload_url
from superdesk.core.web import Response, EndpointGroup, Request
from superdesk.media.media_operations import guess_media_extension
from superdesk.core.resources import ResourceModel, ResourceConfig

# from newsroom.decorator import is_valid_session, clear_session_and_redirect_to_login


CACHE_MAX_AGE = 3600 * 24 * 7  # 7 days
ASSETS_RESOURCE = "upload"
upload_endpoints = EndpointGroup(ASSETS_RESOURCE, __name__)


def get_file(key):
    file = request.files.get(key)
    if file:
        filename = secure_filename(file.filename)
        get_current_app().media.put(file, resource=ASSETS_RESOURCE, _id=filename, content_type=file.content_type)
        return url_for("upload.get_upload", media_id=filename)


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


class RouteArguments(BaseModel):
    media_id: str


@upload_endpoints.endpoint("/assets/<string:media_id>", methods=["GET"])
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


def init_app(app):
    app.upload_url = upload_url
    app.config["DOMAIN"].setdefault(
        "upload",
        {
            "authentication": None,
            "mongo_prefix": newsroom.MONGO_PREFIX,
            "internal_resource": True,
        },
    )


class Upload(ResourceModel):
    # NOTE: Temporary resource so `GridFSMediaStorageAsync` would work
    # we should remove once Upload resource is implemented  on `superdesk-core`
    pass


upload_model_config = ResourceConfig(
    name="upload",
    data_class=Upload,
    elastic=None,
)

module = Module(name="newsroom.upload", resources=[upload_model_config], endpoints=[upload_endpoints])
