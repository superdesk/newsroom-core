import superdesk

from quart_babel import gettext

from superdesk.core import get_current_app
from superdesk.flask import abort, Blueprint, request

from newsroom.assets import get_upload
from newsroom.news_api.utils import post_api_audit


blueprint = Blueprint("assets", __name__)


def init_app(app):
    superdesk.blueprint(blueprint, app)


@blueprint.route("/assets/<path:asset_id>", methods=["GET"])
async def get_item(asset_id):
    app = get_current_app()
    auth = app.auth
    if not auth.authorized([], None, request.method):
        return abort(401, gettext("Invalid token"))

    post_api_audit({"_items": [{"_id": asset_id}]})
    response = await get_upload(asset_id)
    return response if response else abort(404)
