import re
from typing import Any

from bson import ObjectId
from pydantic import BaseModel

from superdesk.core import json
from superdesk.cache import cache
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


async def get_nav_data_from_request(request: Request) -> dict[str, Any]:
    form_data = await request.get_form()
    nav_data = form_data.get("navigation")
    if nav_data is None:
        await request.abort(400)

    return json.loads(nav_data)


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
async def create(request: Request):
    nav_data = await get_nav_data_from_request(request)
    service = NavigationsService()

    creation_data = await prepare_navigation_data(nav_data)
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

    data = await get_nav_data_from_request(request)
    updates = await prepare_navigation_data(data)
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


async def prepare_navigation_data(data: dict[str, Any]) -> dict[str, Any]:
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
