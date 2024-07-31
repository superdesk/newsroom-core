import os

from pydantic import BaseModel
import newsroom
import bson.errors
from typing import cast

from werkzeug.wsgi import wrap_file
from werkzeug.utils import secure_filename

from superdesk.core.module import Module
from superdesk.upload import upload_url as _upload_url
from superdesk.core import get_current_app, get_app_config
from superdesk.core.web import Response, EndpointGroup
from superdesk.flask import request, url_for, Blueprint, abort
from superdesk.core.elastic.common import ElasticResourceConfig
from superdesk.core.resources import ResourceModel, ResourceConfig
from superdesk.media.media_operations import guess_media_extension

from newsroom.decorator import is_valid_session, clear_session_and_redirect_to_login


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


def construct_response(media_file):
    app = get_current_app()
    data = wrap_file(request.environ, media_file, buffer_size=1024 * 256)

    response = app.response_class(data, mimetype=media_file.content_type, direct_passthrough=True)
    response.content_length = media_file.length
    response.last_modified = media_file.upload_date
    response.set_etag(media_file.md5)
    response.cache_control.max_age = CACHE_MAX_AGE
    response.cache_control.s_max_age = CACHE_MAX_AGE
    response.cache_control.public = True
    response.make_conditional(request, accept_ranges=True, complete_length=media_file.length)

    return response


def set_filename_in_response(response, filename, media_file):
    if filename:
        _filename, ext = os.path.splitext(filename)
        if not ext:
            ext = guess_media_extension(media_file.content_type)
        filename = secure_filename(f"{_filename}{ext}")
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    else:
        response.headers["Content-Disposition"] = "inline"


class RouteArguments(BaseModel):
    media_id: str

@upload_endpoints.endpoint("/assets/<string:media_id>", methods=["GET"])
async def get_upload(args: RouteArguments, _p, _r) -> Response:
    print('*' * 100)
    print(args)

    # if not get_app_config("PUBLIC_DASHBOARD") and not is_valid_session():
    #     return clear_session_and_redirect_to_login()

    media_file = await get_media_file(args.media_id)
    if not media_file:
        abort(404)

    # import pdb; pdb.set_trace()

    content = await media_file.read()

    # response = construct_response(media_file)
    # filename = request.args.get("filename")
    # set_filename_in_response(response, filename, media_file)
    return Response(content, 200, ())


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
