import re

from bson import ObjectId
from pydantic import BaseModel
from quart_babel import gettext

from superdesk.core import json
from superdesk.cache import cache
from superdesk.flask import jsonify, request
from superdesk.core.web import EndpointGroup, Response, Request

from newsroom.decorator import admin_only
from newsroom.utils import query_resource
from newsroom.core import get_current_wsgi_app
from newsroom.flask import get_file_from_request
from newsroom.assets import save_file_and_get_url

from .service import NavigationsService


navigations_endpoints = EndpointGroup("navigations", __name__)


async def get_navigations_as_list():
    return [obj async for obj in NavigationsService().get_all_raw()]


async def get_settings_data():
    all_navigations = await get_navigations_as_list()

    return {
        "products": list(query_resource("products")),
        "navigations": all_navigations,
        "sections": [
            s for s in get_current_wsgi_app().sections if s.get("_id") != "monitoring"
        ],  # monitoring has no navigation
    }


class SearchParams(BaseModel):
    q: str | None = None


class RouteArguments(BaseModel):
    id: str


@navigations_endpoints.endpoint("/navigations", methods=["GET"])
async def index():
    navigations = await get_navigations_as_list()
    return Response(navigations)


@navigations_endpoints.endpoint("/navigations/search", methods=["GET"])
async def search(_a, params: SearchParams, _q):
    lookup = None
    if params.q:
        regex = re.compile(".*{}.*".format(params.q), re.IGNORECASE)
        lookup = {"name": regex}
    cursor = await NavigationsService().search(lookup)
    navigations = await cursor.to_list_raw()
    return Response(navigations)


@navigations_endpoints.endpoint("/navigations/new", methods=["POST"])
@admin_only
async def create():
    data = json.loads((await request.form)["navigation"])

    if not data.get("name"):
        return jsonify(gettext("Name not found")), 400

    service = NavigationsService()
    creation_data = await _get_navigation_data(data)
    creation_data["id"] = service.generate_id()
    product_ids = creation_data.pop("products", [])
    created_ids = await service.create([creation_data])

    if product_ids is not None:
        await add_remove_products_for_navigation(ObjectId(created_ids[0]), product_ids)
    return Response({"success": True, "_id": created_ids[0]}, 201)


@navigations_endpoints.endpoint("/navigations/<string:id>", methods=["POST"])
@admin_only
async def edit(args: RouteArguments, _p: None, request: Request):
    service = NavigationsService()
    nav = await service.find_by_id(args.id)

    if not nav:
        await request.abort(404)

    data = json.loads((await request.form)["navigation"])
    updates = await _get_navigation_data(data)
    product_ids = updates.pop("products", [])

    await service.update(args.id, updates)
    if product_ids is not None:
        await add_remove_products_for_navigation(nav.id, product_ids)
    return Response({"success": True})


@navigations_endpoints.endpoint("/navigations/<string:id>", methods=["DELETE"])
@admin_only
async def delete(args: RouteArguments, _p: None, request: Request):
    service = NavigationsService()
    nav = await service.find_by_id(args.id)
    if not nav:
        await request.abort(404)
    await service.delete(nav)
    return Response({"success": True})


async def _get_navigation_data(data):
    navigation_data = {
        "name": data.get("name"),
        "description": data.get("description", ""),
        "is_enabled": data.get("is_enabled"),
        "product_type": data.get("product_type", "wire"),
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


async def add_remove_products_for_navigation(nav_id: ObjectId, product_ids: list[str]):
    products = query_resource("products")
    db = get_current_wsgi_app().data.get_mongo_collection("products")

    for product in products:
        if str(product["_id"]) in product_ids:
            db.update_one({"_id": product["_id"]}, {"$addToSet": {"navigations": nav_id}})
        else:
            db.update_one({"_id": product["_id"]}, {"$pull": {"navigations": nav_id}})

    cache.clean(["products"])
