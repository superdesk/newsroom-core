import re

import flask
from bson import ObjectId
from flask import jsonify, json, current_app as app
from flask_babel import gettext
from superdesk import get_resource_service

from newsroom.decorator import admin_only, login_required
from newsroom.cards import blueprint
from newsroom.utils import (
    get_entity_or_404,
    query_resource,
    set_original_creator,
    set_version_creator,
)
from newsroom.upload import get_file
from newsroom.wire.views import delete_dashboard_caches


def get_settings_data():
    return {
        "products": list(query_resource("products", lookup={"is_enabled": True})),
        "cards": list(query_resource("cards")),
        "dashboards": app.dashboards,
        "navigations": list(query_resource("navigations", lookup={"is_enabled": True})),
    }


@blueprint.route("/cards", methods=["GET"])
@login_required
def index():
    cards = list(query_resource("cards", lookup=None))
    return jsonify(cards), 200


@blueprint.route("/cards/search", methods=["GET"])
@admin_only
def search():
    lookup = None
    if flask.request.args.get("q"):
        regex = re.compile(".*{}.*".format(flask.request.args.get("q")), re.IGNORECASE)
        lookup = {"label": regex}
    products = list(query_resource("cards", lookup=lookup))
    return jsonify(products), 200


@blueprint.route("/cards/new", methods=["POST"])
@admin_only
def create():
    data = json.loads(flask.request.form["card"])
    card_data = _get_card_data(data)
    set_original_creator(card_data)
    ids = get_resource_service("cards").post([card_data])
    delete_dashboard_caches()
    return jsonify({"success": True, "_id": ids[0]}), 201


def _get_card_data(data):
    if not data:
        flask.abort(400)

    if not data.get("label"):
        raise ValueError(gettext("Label not found"))

    if not data.get("type"):
        raise ValueError(gettext("Type not found"))

    if data.get("dashboard") and data["dashboard"] not in {d["_id"] for d in app.dashboards}:
        raise ValueError(gettext("Dashboard type not found"))

    card_data = {
        "label": data.get("label"),
        "type": data.get("type"),
        "dashboard": data.get("dashboard", "newsroom"),
        "config": data.get("config"),
        "order": int(data.get("order", 0) or 0),
    }

    if data.get("type") == "2x2-events":
        for index, event in enumerate(card_data["config"]["events"]):
            file_url = get_file("file{}".format(index))
            if file_url:
                event["file_url"] = file_url

    if data.get("type") == "4-photo-gallery":
        for source in (data.get("config") or {}).get("sources"):
            if source.get("url") and source.get("count"):
                source["count"] = int(source.get("count")) if source.get("count") else source.get("count")
            else:
                source.pop("url", None)
                source.pop("count", None)

    return card_data


@blueprint.route("/cards/<id>", methods=["POST"])
@admin_only
def edit(id):
    get_entity_or_404(id, "cards")

    data = json.loads(flask.request.form["card"])
    card_data = _get_card_data(data)
    set_version_creator(card_data)
    get_resource_service("cards").patch(id=ObjectId(id), updates=card_data)
    delete_dashboard_caches()
    return jsonify({"success": True}), 200


@blueprint.route("/cards/<id>", methods=["DELETE"])
@admin_only
def delete(id):
    """Deletes the cards by given id"""
    get_entity_or_404(id, "cards")
    get_resource_service("cards").delete({"_id": ObjectId(id)})
    delete_dashboard_caches()
    return jsonify({"success": True}), 200
