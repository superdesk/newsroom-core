from typing import Dict
import re
import ipaddress

import flask
import werkzeug.exceptions

from bson import ObjectId
from datetime import datetime
from flask import jsonify, current_app as app
from flask_babel import gettext
from superdesk import get_resource_service
from werkzeug.exceptions import NotFound, BadRequest

from newsroom.decorator import admin_only, account_manager_only, login_required
from newsroom.companies import blueprint
from newsroom.types import AuthProviderConfig
from newsroom.utils import (
    get_public_user_data,
    query_resource,
    find_one,
    get_json_or_400,
    set_original_creator,
    set_version_creator,
)


def get_company_types_options(company_types):
    return [dict([(k, v) for k, v in company_type.items() if k in {"id", "name"}]) for company_type in company_types]


def get_settings_data():
    def render_provider(provider: AuthProviderConfig) -> Dict[str, str]:
        return {
            "_id": provider["_id"],
            "name": str(provider["name"]),
            "auth_type": provider["auth_type"].value,
        }

    return {
        "companies": list(query_resource("companies")),
        "services": app.config["SERVICES"],
        "products": list(query_resource("products")),
        "sections": app.sections,
        "company_types": get_company_types_options(app.config.get("COMPANY_TYPES", [])),
        "api_enabled": app.config.get("NEWS_API_ENABLED", False),
        "ui_config": get_resource_service("ui_config").get_section_config("companies"),
        "countries": app.countries,
        "auth_providers": [render_provider(provider) for provider in app.config.get("AUTH_PROVIDERS") or []],
    }


@blueprint.route("/companies/search", methods=["GET"])
@account_manager_only
def search():
    lookup = None
    if flask.request.args.get("q"):
        regex = re.compile(".*{}.*".format(flask.request.args.get("q")), re.IGNORECASE)
        lookup = {"name": regex}
    companies = list(query_resource("companies", lookup=lookup))
    return jsonify(companies), 200


@blueprint.route("/companies/new", methods=["POST"])
@account_manager_only
def create():
    company = get_json_or_400()
    errors = get_errors_company(company)
    if errors:
        return errors

    new_company = get_company_updates(company)
    set_original_creator(new_company)
    try:
        ids = get_resource_service("companies").post([new_company])
    except werkzeug.exceptions.Conflict:
        return conflict_error(new_company)

    return jsonify({"success": True, "_id": ids[0]}), 201


def get_errors_company(updates, original=None):
    if original is None:
        original = {}

    if not (updates.get("name") or original.get("name")):
        return jsonify({"name": gettext("Name not found")}), 400

    if updates.get("allowed_ip_list"):
        errors = []
        for ip in updates["allowed_ip_list"]:
            try:
                ipaddress.ip_network(ip, strict=True)
            except ValueError as e:
                errors.append(gettext("{0}: {1}".format(ip, e)))

        if errors:
            return jsonify({"allowed_ip_list": errors}), 400


def get_company_updates(data, original=None):
    if original is None:
        original = {}

    updates = {
        "name": data.get("name") or original.get("name"),
        "url": data.get("url") or original.get("url"),
        "sd_subscriber_id": data.get("sd_subscriber_id") or original.get("sd_subscriber_id"),
        "account_manager": data.get("account_manager") or original.get("account_manager"),
        "contact_name": data.get("contact_name") or original.get("contact_name"),
        "contact_email": data.get("contact_email") or original.get("contact_email"),
        "phone": data.get("phone") or original.get("phone"),
        "country": data.get("country") or original.get("country"),
        "is_enabled": data.get("is_enabled", original.get("is_enabled")),
        "company_type": data.get("company_type") or original.get("company_type"),
        "monitoring_administrator": data.get("monitoring_administrator") or original.get("monitoring_administrator"),
        "allowed_ip_list": data.get("allowed_ip_list") or original.get("allowed_ip_list"),
        "auth_domains": data.get("auth_domains"),
        "auth_provider": data.get("auth_provider") or original.get("auth_provider") or "newshub",
    }

    for field in [
        "sections",
        "archive_access",
        "events_only",
        "restrict_coverage_info",
        "products",
        "seats",
        "internal",
    ]:
        if field in data:
            updates[field] = data[field]

    for product in updates.get("products") or []:
        product["_id"] = ObjectId(product["_id"])
        product.setdefault("seats", 0)

    if data.get("expiry_date"):
        updates["expiry_date"] = datetime.strptime(str(data.get("expiry_date"))[:10], "%Y-%m-%d")
    else:
        updates["expiry_date"] = None

    return updates


@blueprint.route("/companies/<_id>", methods=["GET", "POST"])
@account_manager_only
def edit(_id):
    original = find_one("companies", _id=ObjectId(_id))

    if not original:
        return NotFound(gettext("Company not found"))

    if flask.request.method == "POST":
        company = get_json_or_400()
        errors = get_errors_company(company, original)
        if errors:
            return errors

        updates = get_company_updates(company, original)
        set_version_creator(updates)
        try:
            get_resource_service("companies").patch(ObjectId(_id), updates=updates)
        except werkzeug.exceptions.Conflict:
            return conflict_error(updates)
        app.cache.delete(_id)
        return jsonify({"success": True}), 200
    return jsonify(original), 200


def conflict_error(updates):
    if updates.get("auth_domains"):
        return jsonify({"auth_domains": gettext("Value is already used")}), 400
    else:
        return jsonify({"name": gettext("Company already exists")}), 400


@blueprint.route("/companies/<_id>", methods=["DELETE"])
@admin_only
def delete(_id):
    """
    Deletes the company and users of the company with given company id
    """
    try:
        get_resource_service("users").delete_action(lookup={"company": ObjectId(_id)})
    except BadRequest as er:
        return jsonify({"error": er.description}), 403
    get_resource_service("companies").delete_action(lookup={"_id": ObjectId(_id)})

    app.cache.delete(_id)
    return jsonify({"success": True}), 200


@blueprint.route("/companies/<_id>/users", methods=["GET"])
@login_required
def company_users(_id):
    users = [get_public_user_data(user) for user in query_resource("users", lookup={"company": ObjectId(_id)})]
    return jsonify(users)


@blueprint.route("/companies/<company_id>/approve", methods=["POST"])
@account_manager_only
def approve_company(company_id):
    original = find_one("companies", _id=ObjectId(company_id))
    if not original:
        return NotFound(gettext("Company not found"))

    if original.get("is_approved"):
        return jsonify({"error": gettext("Company is already approved")}), 403

    # Activate this Company
    updates = {
        "is_enabled": True,
        "is_approved": True,
    }
    get_resource_service("companies").patch(original["_id"], updates=updates)

    # Activate the Users of this Company
    users_service = get_resource_service("users")
    for user in users_service.get(req=None, lookup={"company": original["_id"], "is_approved": {"$ne": True}}):
        users_service.approve_user(user)

    return {"success": True}


def get_product_updates(updates: Dict[str, bool], seats: Dict[str, int]):
    product_ids = [product_id for product_id, selected in updates.items() if selected]
    if not product_ids:
        return []
    products = list(query_resource("products", lookup={"_id": {"$in": product_ids}}))
    return [
        {
            "_id": product["_id"],
            "section": product.get("product_type") or "wire",
            "seats": seats.get(str(product["_id"])) or 0,
        }
        for product in products
    ]
