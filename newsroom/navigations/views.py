import re
from typing import List

from bson import ObjectId
from quart_babel import gettext

from newsroom.flask import get_file_from_request
from superdesk.core import get_current_app, json
from superdesk.flask import jsonify, request
from superdesk import get_resource_service
from superdesk.cache import cache

from newsroom.decorator import admin_only
from newsroom.navigations import blueprint
from newsroom.utils import (
    get_entity_or_404,
    query_resource,
    set_original_creator,
    set_version_creator,
)
from newsroom.assets import save_file_and_get_url


def get_settings_data():
    return {
        "products": list(query_resource("products")),
        "navigations": list(query_resource("navigations")),
        "sections": [
            s for s in get_current_app().as_any().sections if s.get("_id") != "monitoring"
        ],  # monitoring has no navigation
    }


@blueprint.route("/navigations", methods=["GET"])
def index():
    navigations = list(query_resource("navigations", lookup=None))
    return jsonify(navigations), 200


@blueprint.route("/navigations/search", methods=["GET"])
def search():
    lookup = None
    if request.args.get("q"):
        regex = re.compile(".*{}.*".format(request.args.get("q")), re.IGNORECASE)
        lookup = {"name": regex}
    products = list(query_resource("navigations", lookup=lookup))
    return jsonify(products), 200


@blueprint.route("/navigations/new", methods=["POST"])
@admin_only
async def create():
    data = json.loads((await request.form)["navigation"])
    nav_data = await _get_navigation_data(data)
    product_ids = nav_data.pop("products", [])

    set_original_creator(nav_data)
    ids = get_resource_service("navigations").post([nav_data])

    if product_ids is not None:
        add_remove_products_for_navigation(ObjectId(ids[0]), product_ids)

    return jsonify({"success": True, "_id": ids[0]}), 201


async def _get_navigation_data(data):
    if not data.get("name"):
        return jsonify(gettext("Name not found")), 400

    navigation_data = {
        "name": data.get("name"),
        "description": data.get("description"),
        "is_enabled": data.get("is_enabled"),
        "product_type": data.get("product_type"),
        "tile_images": data.get("tile_images"),
        "products": data.get("products"),
    }

    for index, tile in enumerate(navigation_data["tile_images"] or []):
        file = await get_file_from_request(f"file{index}")

        if file:
            file_url = await save_file_and_get_url(f"file{index}")
            if file_url:
                tile["file_url"] = file_url

    return navigation_data


@blueprint.route("/navigations/<_id>", methods=["POST"])
@admin_only
async def edit(_id):
    get_entity_or_404(_id, "navigations")

    data = json.loads((await request.form)["navigation"])
    nav_data = await _get_navigation_data(data)
    product_ids = nav_data.pop("products", [])

    set_version_creator(nav_data)
    get_resource_service("navigations").patch(id=ObjectId(_id), updates=nav_data)

    if product_ids is not None:
        add_remove_products_for_navigation(ObjectId(_id), product_ids)

    return jsonify({"success": True}), 200


@blueprint.route("/navigations/<_id>", methods=["DELETE"])
@admin_only
async def delete(_id):
    """Deletes the navigations by given id"""
    get_entity_or_404(_id, "navigations")
    get_resource_service("navigations").delete_action({"_id": ObjectId(_id)})
    return jsonify({"success": True}), 200


def add_remove_products_for_navigation(nav_id: ObjectId, product_ids: List[str]):
    get_entity_or_404(nav_id, "navigations")
    products = query_resource("products")
    db = get_current_app().data.get_mongo_collection("products")
    for product in products:
        if str(product["_id"]) in product_ids:
            db.update_one({"_id": product["_id"]}, {"$addToSet": {"navigations": nav_id}})
        else:
            db.update_one({"_id": product["_id"]}, {"$pull": {"navigations": nav_id}})
    cache.clean(["products"])
