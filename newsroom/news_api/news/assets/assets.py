import superdesk
import bson.errors
from io import BytesIO
from datetime import datetime, timezone, timedelta

from quart_babel import gettext

from superdesk.core import get_current_app
from superdesk.flask import abort, Blueprint, request

from newsroom.assets import ASSETS_RESOURCE
from newsroom.news_api.utils import post_api_audit


blueprint = Blueprint("assets", __name__)
cache_for = 3600 * 24 * 7  # 7 days cache


def init_app(app):
    superdesk.blueprint(blueprint, app)


@blueprint.route("/assets/<path:asset_id>", methods=["GET"])
async def get_item(asset_id):
    app = get_current_app()
    auth = app.auth
    if not auth.authorized([], None, request.method):
        return abort(401, gettext("Invalid token"))

    try:
        media_file = await app.media_async.get(asset_id, resource=ASSETS_RESOURCE)
    except bson.errors.InvalidId:
        media_file = None
    if not media_file:
        abort(404)

    file_body = app.as_any().response_class.io_body_class(BytesIO(media_file.read()))
    response = app.response_class(file_body, mimetype=media_file.content_type)
    response.content_length = media_file.length
    response.last_modified = media_file.upload_date
    response.set_etag(media_file.md5)
    response.cache_control.max_age = cache_for
    response.cache_control.s_max_age = cache_for
    response.cache_control.public = True
    response.expires = datetime.now(timezone.utc) + timedelta(seconds=cache_for)
    response.headers["Content-Disposition"] = "inline"

    await response.make_conditional(request, accept_ranges=True, complete_length=media_file.length)

    post_api_audit({"_items": [{"_id": asset_id}]})
    return response
