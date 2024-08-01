import bson.errors
from werkzeug.wsgi import wrap_file
from flask_babel import gettext

from superdesk.core import get_current_app
from superdesk.flask import abort, Blueprint, request
import superdesk

from newsroom.assets.module import ASSETS_RESOURCE
from newsroom.news_api.utils import post_api_audit


blueprint = Blueprint("assets", __name__)


def init_app(app):
    superdesk.blueprint(blueprint, app)


@blueprint.route("/assets/<path:asset_id>", methods=["GET"])
def get_item(asset_id):
    app = get_current_app()
    auth = app.auth
    if not auth.authorized([], None, request.method):
        return abort(401, gettext("Invalid token"))

    try:
        media_file = app.media.get(asset_id, ASSETS_RESOURCE)
    except bson.errors.InvalidId:
        media_file = None
    if not media_file:
        abort(404)

    data = wrap_file(request.environ, media_file, buffer_size=1024 * 256)
    response = app.response_class(data, mimetype=media_file.content_type, direct_passthrough=True)
    response.content_length = media_file.length
    response.last_modified = media_file.upload_date
    response.set_etag(media_file.md5)
    response.make_conditional(request)
    response.headers["Content-Disposition"] = "inline"
    post_api_audit({"_items": [{"_id": asset_id}]})
    return response
