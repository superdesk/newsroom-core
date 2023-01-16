import re
from typing import List

import flask
from bson import ObjectId
from flask import jsonify, current_app
from flask_babel import gettext
from superdesk import get_resource_service

from newsroom.decorator import admin_only, account_manager_only
from newsroom.products import blueprint
from newsroom.products.products import get_products_by_company
from newsroom.types import Product, ProductRef
from newsroom.utils import (
    get_json_or_400,
    get_entity_or_404,
    set_original_creator,
    set_version_creator,
    query_resource,
)


def get_settings_data():
    return {
        "products": list(query_resource("products")),
        "navigations": list(query_resource("navigations")),
        "companies": list(query_resource("companies")),
        "sections": [s for s in current_app.sections if s.get("_id") != "monitoring"],  # monitoring has no products
    }


def get_product_ref(product: Product) -> ProductRef:
    assert "_id" in product
    return {
        "_id": product["_id"],
        "section": product.get("product_type") or "wire",
    }


@blueprint.route("/products", methods=["GET"])
@admin_only
def index():
    lookup = None
    if flask.request.args.get("q"):
        lookup = flask.request.args.get("q")
    products = list(query_resource("products", lookup=lookup))
    return jsonify(products), 200


@blueprint.route("/products/search", methods=["GET"])
@account_manager_only
def search():
    lookup = None
    if flask.request.args.get("q"):
        regex = re.compile(".*{}.*".format(flask.request.args.get("q")), re.IGNORECASE)
        lookup = {"name": regex}
    products = list(query_resource("products", lookup=lookup))
    return jsonify(products), 200


def validate_product(product):
    if not product.get("name"):
        return jsonify({"name": gettext("Name not found")}), 400


@blueprint.route("/products/new", methods=["POST"])
@admin_only
def create():
    product = get_json_or_400()

    validation = validate_product(product)
    if validation:
        return validation

    if product.get("navigations"):
        product["navigations"] = [
            ObjectId(get_entity_or_404(_id, "navigations")["_id"]) for _id in product.get("navigations")
        ]
    set_original_creator(product)
    ids = get_resource_service("products").post([product])
    return jsonify({"success": True, "_id": ids[0]}), 201


@blueprint.route("/products/<id>", methods=["POST"])
@admin_only
def edit(id):
    get_entity_or_404(ObjectId(id), "products")
    data = get_json_or_400()
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
def update_companies(id):
    updates = flask.request.get_json()
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
            get_resource_service("companies").patch(company["_id"], updates={"products": company_products})
    return jsonify({"success": True}), 200


@blueprint.route("/products/<id>/navigations", methods=["POST"])
@admin_only
def update_navigations(id):
    updates = flask.request.get_json()
    if updates.get("navigations"):
        updates["navigations"] = [ObjectId(nav_id) for nav_id in updates["navigations"]]
    get_resource_service("products").patch(id=ObjectId(id), updates=updates)
    return jsonify({"success": True}), 200


@blueprint.route("/products/<id>", methods=["DELETE"])
@admin_only
def delete(id):
    """Deletes the products by given id"""
    get_entity_or_404(ObjectId(id), "products")
    get_resource_service("products").delete_action({"_id": ObjectId(id)})
    return jsonify({"success": True}), 200
