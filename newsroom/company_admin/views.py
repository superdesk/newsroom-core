from typing import List
from bson import ObjectId

from werkzeug.exceptions import NotFound
from quart_babel import gettext

from superdesk.core import get_current_app, get_app_config
from superdesk.flask import render_template, jsonify
from superdesk.utc import utcnow, utc_to_local

from newsroom.auth.utils import get_user_from_request, get_company_from_request, get_auth_providers
from newsroom.decorator import login_required, company_admin_only
from newsroom.types import Company, Product
from newsroom.utils import query_resource, get_json_or_400
from newsroom.company_admin import blueprint
from newsroom.email import send_template_email
from newsroom.settings import get_settings_collection, GENERAL_SETTINGS_LOOKUP
from newsroom.users import get_user_profile_data


@blueprint.route("/company_admin")
@login_required
@company_admin_only
async def index():
    user_profile_data = await get_user_profile_data()
    return await render_template("company_admin_index.html", data=get_view_data(), user_profile_data=user_profile_data)


def filter_disabled_products(company: Company, products: List[Product]) -> Company:
    product_ids = set([p["_id"] for p in products])
    if company.get("products"):
        company["products"] = [ref for ref in company["products"] if ref["_id"] in product_ids]
    return company


def get_view_data():
    company = get_company_from_request(None)
    assert company is not None
    company_users = list(query_resource("users", lookup={"company": company.id}))
    products = list(query_resource("products", lookup={"is_enabled": True}))
    app = get_current_app().as_any()

    return {
        "users": company_users,
        "companyId": str(company.id),
        "companies": [filter_disabled_products(company.to_dict(), products)],
        "sections": app.sections,
        "products": products,
        "countries": app.countries,
        "auth_provider_features": {key: provider.features for key, provider in get_auth_providers().items()},
    }


@blueprint.route("/company_admin/send_product_seat_request", methods=["POST"])
@login_required
@company_admin_only
async def send_product_seat_request_email():
    user = get_user_from_request(None)
    company = get_company_from_request(None)

    if not company:
        return NotFound(gettext("Company not found"))

    data = await get_json_or_400()

    errors = []
    if not len(data.get("product_ids", [])):
        errors.append(gettext("No products selected"))

    if (data.get("number_of_seats") or 0) < 1:
        errors.append(gettext("Invalid number of seats requested"))

    if len(errors):
        return jsonify({"errors": errors}), 400

    products = list(
        query_resource(
            "products", lookup={"_id": {"$in": [ObjectId(product_id) for product_id in data["product_ids"]]}}
        )
    )

    general_settings = get_settings_collection().find_one(GENERAL_SETTINGS_LOOKUP)
    if not general_settings:
        return NotFound(gettext("Product Seat Request recipients not configured"))

    recipients = [
        address
        for address in (general_settings.get("values").get("product_seat_request_recipients") or "").split(",")
        if address
    ]
    if not len(recipients):
        return NotFound(gettext("Product Seat Request recipients not configured"))

    await send_template_email(
        to=recipients,
        template="additional_product_seat_request_email",
        template_kwargs=dict(
            app_name=get_app_config("SITE_NAME"),
            products=products,
            number_of_seats=data["number_of_seats"],
            note=data["note"],
            user=user.to_dict(),
            company=company.to_dict(),
            now=utc_to_local(get_app_config("DEFAULT_TIMEZONE"), utcnow()),
            all_products=len(products) == len(company.products or []),
        ),
    )

    return jsonify({"success": True}), 200
