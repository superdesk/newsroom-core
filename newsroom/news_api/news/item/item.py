from bson import ObjectId
from flask_babel import gettext

import superdesk
from superdesk.core import get_current_app
from superdesk.flask import abort, g, Blueprint, request
from superdesk import get_resource_service
from newsroom.news_api.utils import post_api_audit


blueprint = Blueprint("news/item", __name__)


def init_app(app):
    superdesk.blueprint(blueprint, app)


@blueprint.route("/news/item/<path:item_id>", methods=["GET"])
def get_item(item_id):
    app = get_current_app()
    auth = app.auth
    if not auth.authorized([], None, request.method):
        return abort(401, gettext("Invalid token"))

    _format = request.args.get("format", "NINJSFormatter")
    _version = request.args.get("version")
    service = get_resource_service("formatters")
    formatted = service.get_version(item_id, _version, _format)
    mimetype = formatted.get("mimetype")
    response = app.response_class(response=formatted.get("formatted_item"), status=200, mimetype=mimetype)

    post_api_audit({"_items": [{"_id": item_id}]})
    # Record the retrieval of the item in the history collection
    get_resource_service("history").create_history_record(
        [{"_id": item_id, "version": formatted.get("version")}],
        "api",
        {"_id": None, "company": ObjectId(g.company_id)},
        "news_api",
    )
    return response
