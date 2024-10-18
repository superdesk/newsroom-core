from typing import List
from bson import ObjectId

from quart_babel import gettext

from superdesk.core.web import EndpointGroup
from superdesk.core.types import Response, Request
from superdesk.core import get_app_config
from superdesk.flask import render_template
from superdesk.utc import utcnow, utc_to_local

from newsroom.auth import auth_rules
from newsroom.types import Company, Product
from newsroom.core import get_current_wsgi_app
from newsroom.email import send_template_email
from newsroom.users import get_user_profile_data
from newsroom.companies.utils import get_users_by_company
from newsroom.utils import get_json_or_400_async, query_resource
from newsroom.settings import get_settings_collection, GENERAL_SETTINGS_LOOKUP
from newsroom.auth.utils import get_user_from_request, get_company_from_request, get_auth_providers

blueprint = EndpointGroup("company_admin", __name__)


@blueprint.endpoint("/company_admin", auth=[auth_rules.company_admin_only])
async def index():
    user_profile_data = await get_user_profile_data()
    return await render_template(
        "company_admin_index.html", data=(await get_view_data()), user_profile_data=user_profile_data
    )


def filter_disabled_products(company: Company, products: List[Product]) -> Company:
    product_ids = set([str(p["_id"]) for p in products])
    if company.get("products"):
        company["products"] = [ref for ref in company["products"] if str(ref["_id"]) in product_ids]
    return company


async def get_view_data():
    company = get_company_from_request(None)
    assert company is not None
    company_users = await get_users_by_company(company.id)

    # TODO-ASYNC: revisit when `products` is converted to async
    products = list(query_resource("products", lookup={"is_enabled": True}))
    app = get_current_wsgi_app()

    return {
        "users": await company_users.to_list_raw(),
        "companyId": str(company.id),
        "companies": [filter_disabled_products(company.to_dict(), products)],
        "sections": app.sections,
        "products": products,
        "countries": app.countries,
        "auth_provider_features": {key: provider.features for key, provider in get_auth_providers().items()},
    }


@blueprint.endpoint("/company_admin/send_product_seat_request", methods=["POST"], auth=[auth_rules.company_admin_only])
async def send_product_seat_request_email(request: Request):
    user = get_user_from_request(None)
    company = get_company_from_request(None)

    if not company:
        await request.abort(404, gettext("Company not found"))

    errors = []
    data = await get_json_or_400_async(request)
    if not len(data.get("product_ids", [])):
        errors.append(gettext("No products selected"))

    if (data.get("number_of_seats") or 0) < 1:
        errors.append(gettext("Invalid number of seats requested"))

    if len(errors):
        return Response({"errors": errors}, 400)

    # TODO-ASYNC: revisit when `products` is converted to async
    products = list(
        query_resource(
            "products", lookup={"_id": {"$in": [ObjectId(product_id) for product_id in data["product_ids"]]}}
        )
    )

    general_settings = get_settings_collection().find_one(GENERAL_SETTINGS_LOOKUP)
    if not general_settings:
        await request.abort(404, gettext("Product Seat Request recipients not configured"))

    recipients = [
        address
        for address in (general_settings.get("values").get("product_seat_request_recipients") or "").split(",")
        if address
    ]
    if not len(recipients):
        await request.abort(404, gettext("Product Seat Request recipients not configured"))

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

    return Response({"success": True})
