import re
from typing import List

from bson import ObjectId
from pydantic import BaseModel
from quart_babel import gettext

from newsroom.auth import auth_rules
from newsroom.companies.companies_async.service import CompanyService
from newsroom.core import get_current_wsgi_app
from newsroom.products.service import ProductsService
from superdesk.core.types import Response
from superdesk.core.web import EndpointGroup
from superdesk.flask import jsonify, request, abort
from superdesk import get_resource_service

from newsroom.types import NavigationModel
from newsroom.decorator import admin_only, account_manager_only
from newsroom.navigations import NavigationsService
from newsroom.navigations import get_navigations_as_list
from newsroom.products import blueprint
from newsroom.products.products import get_products_by_company
from newsroom.types import Product, ProductRef
from newsroom.utils import (
    get_json_or_400,
    get_entity_or_404,
    set_original_creator,
    set_version_creator,
)

products_endpoints = EndpointGroup("products_views", __name__)


async def get_settings_data():
    app = get_current_wsgi_app()

    return {
        "products": await ProductsService().get_all_raw_as_list(),
        "navigations": await get_navigations_as_list(),
        "companies": await CompanyService().get_all_raw_as_list(),
        "sections": [s for s in app.sections if s.get("_id") != "monitoring"],  # monitoring has no products
    }


def get_product_ref(product: Product, seats=0) -> ProductRef:
    assert "_id" in product
    return {
        "_id": product["_id"],
        "section": product.get("product_type") or "wire",
        "seats": seats or 0,
    }


@products_endpoints.endpoint("/products", methods=["GET"], auth=[auth_rules.admin_only])
async def index():
    products = await ProductsService().get_all_raw_as_list()
    return Response(products)


class SearchArgs(BaseModel):
    q: str | None = None


@products_endpoints.endpoint(
    "/products/search", methods=["GET"], auth=[auth_rules.account_manager_or_company_admin_only]
)
async def search(_a: None, params: SearchArgs, _r: None):
    lookup = {}
    if params.q:
        regex = re.compile(".*{}.*".format(params.q), re.IGNORECASE)
        lookup = {"name": regex}

    search_cursor = await ProductsService().search(lookup)
    products = await search_cursor.to_list_raw()

    return Response(products)


def validate_product(product):
    if not product.get("name"):
        return jsonify({"name": gettext("Name not found")}), 400


async def find_nav_or_404(nav_id: str) -> NavigationModel:
    nav = await NavigationsService().find_by_id(nav_id)
    if nav is None:
        abort(404)
    return nav


@blueprint.route("/products/new", methods=["POST"])
@admin_only
async def create():
    product = await get_json_or_400()

    validation = validate_product(product)
    if validation:
        return validation

    if product.get("navigations"):
        # TODO-ASYNC: when products are migrated, we won't need `find_nav_or_404` as it could be replaced with a model validation
        product["navigations"] = [(await find_nav_or_404(_id)).id for _id in product.get("navigations")]
    set_original_creator(product)
    ids = get_resource_service("products").post([product])
    return jsonify({"success": True, "_id": ids[0]}), 201


@blueprint.route("/products/<id>", methods=["POST"])
@admin_only
async def edit(id):
    get_entity_or_404(ObjectId(id), "products")
    data = await get_json_or_400()
    updates = {
        "name": data.get("name"),
        "description": data.get("description"),
        "sd_product_id": data.get("sd_product_id"),
        "query": data.get("query"),
        "planning_item_query": data.get("planning_item_query"),
        "is_enabled": data.get("is_enabled"),
        "product_type": data.get("product_type", "wire"),
    }

    validation = validate_product(updates)
    if validation:
        return validation

    set_version_creator(updates)
    get_resource_service("products").patch(id=ObjectId(id), updates=updates)
    return jsonify({"success": True}), 200


@blueprint.route("/products/<id>/companies", methods=["POST"])
@account_manager_only
async def update_companies(id):
    updates = await request.get_json()
    product = get_entity_or_404(id, "products")
    selected_companies = updates.get("companies") or []
    for company in get_resource_service("companies").get_all():
        update_company = False
        if "products" in company:
            company_products: List[ProductRef] = company["products"].copy()
        else:
            company_products = [get_product_ref(p) for p in get_products_by_company(company)]
            update_company = True
        if str(company["_id"]) in selected_companies:
            for ref in company_products:
                if str(ref["_id"]) == id:
                    break
            else:
                company_products.append(get_product_ref(product))
                update_company = True
        else:
            for ref in company_products:
                if str(ref["_id"]) == id:
                    company_products = [p for p in company_products if str(p["_id"]) != id]
                    update_company = True
        if update_company:
            sections = company.get("sections") or {}
            for product in company_products:
                sections.setdefault(product["section"], True)
            get_resource_service("companies").patch(
                company["_id"], updates={"products": company_products, "sections": sections}
            )
    return jsonify({"success": True}), 200


@blueprint.route("/products/<id>/navigations", methods=["POST"])
@admin_only
async def update_navigations(id):
    updates = await request.get_json()
    if updates.get("navigations"):
        updates["navigations"] = [ObjectId(nav_id) for nav_id in updates["navigations"]]
    get_resource_service("products").patch(id=ObjectId(id), updates=updates)
    return jsonify({"success": True}), 200


@blueprint.route("/products/<id>", methods=["DELETE"])
@admin_only
async def delete(id):
    """Deletes the products by given id"""
    get_entity_or_404(ObjectId(id), "products")
    get_resource_service("products").delete_action({"_id": ObjectId(id)})
    return jsonify({"success": True}), 200
