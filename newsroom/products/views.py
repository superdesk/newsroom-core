import re

from bson import ObjectId
from pydantic import BaseModel
from quart_babel import gettext

from superdesk import get_resource_service
from superdesk.core.web import EndpointGroup
from superdesk.core.types import Request, Response

from newsroom.auth import auth_rules
from newsroom.core import get_current_wsgi_app
from newsroom.types import Product, ProductRef
from newsroom.utils import get_json_or_400_async
from newsroom.products.service import ProductsService
from newsroom.navigations import get_navigations_as_list
from newsroom.companies.companies_async import CompanyService

from .utils import get_products_by_company

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


class SearchParams(BaseModel):
    q: str | None = None


class ProductsArgs(BaseModel):
    product_id: str


@products_endpoints.endpoint("/products", methods=["GET"], auth=[auth_rules.admin_only])
async def index():
    products = await ProductsService().get_all_raw_as_list()
    return Response(products)


@products_endpoints.endpoint(
    "/products/search", methods=["GET"], auth=[auth_rules.account_manager_or_company_admin_only]
)
async def search(_a: None, params: SearchParams, _r: None):
    lookup = {}
    if params.q:
        regex = re.compile(".*{}.*".format(params.q), re.IGNORECASE)
        lookup = {"name": regex}

    search_cursor = await ProductsService().search(lookup)
    products = await search_cursor.to_list_raw()

    return Response(products)


@products_endpoints.endpoint("/products/new", methods=["POST"], auth=[auth_rules.admin_only])
async def create(request: Request):
    creation_data = await get_json_or_400_async(request)
    products = await ProductsService().create([creation_data])
    return Response({"success": True, "_id": products[0]}, 201)


@products_endpoints.endpoint("/products/<string:product_id>", methods=["POST"], auth=[auth_rules.admin_only])
async def edit(args: ProductsArgs, _p: None, request: Request):
    product = await ProductsService().find_by_id(args.product_id)
    if not product:
        await request.abort(404, gettext("Product not found"))

    data = await get_json_or_400_async(request)
    updates = {
        "name": data.get("name"),
        "description": data.get("description"),
        "sd_product_id": data.get("sd_product_id"),
        "query": data.get("query"),
        "planning_item_query": data.get("planning_item_query"),
        "is_enabled": data.get("is_enabled"),
        "product_type": data.get("product_type", "wire"),
    }

    await ProductsService().update(args.product_id, updates)
    return Response({"success": True})


@products_endpoints.endpoint(
    "/products/<string:product_id>/companies", methods=["POST"], auth=[auth_rules.account_manager_only]
)
async def update_companies(args: ProductsArgs, _p: None, request: Request):
    product = await ProductsService().find_by_id(args.product_id)
    if not product:
        await request.abort(404, gettext("Product not found"))

    updates = await request.get_json()
    selected_companies = updates.get("companies") or []

    async for company in CompanyService().get_all_raw():
        update_company = False
        if "products" in company:
            company_products: list[ProductRef] = company["products"].copy()
        else:
            company_products = [get_product_ref(p) for p in await get_products_by_company(company)]
            update_company = True
        if str(company["_id"]) in selected_companies:
            for ref in company_products:
                if str(ref["_id"]) == args.product_id:
                    break
            else:
                company_products.append(get_product_ref(product))
                update_company = True
        else:
            for ref in company_products:
                if str(ref["_id"]) == args.product_id:
                    company_products = [p for p in company_products if str(p["_id"]) != args.product_id]
                    update_company = True
        if update_company:
            sections = company.get("sections") or {}
            for product in company_products:
                sections.setdefault(product["section"], True)
            get_resource_service("companies").patch(
                company["_id"], updates={"products": company_products, "sections": sections}
            )

    return Response({"success": True})


@products_endpoints.endpoint(
    "/products/<string:product_id>/navigations", methods=["POST"], auth=[auth_rules.admin_only]
)
async def update_navigations(args: ProductsArgs, _p: None, request: Request):
    updates = await request.get_json()
    if updates.get("navigations"):
        updates["navigations"] = [ObjectId(nav_id) for nav_id in updates["navigations"]]
    await ProductsService().update(args.product_id, updates)
    return Response({"success": True})


@products_endpoints.endpoint("/products/<string:product_id>", methods=["DELETE"], auth=[auth_rules.admin_only])
async def delete(args: ProductsArgs, _p: None, request: Request):
    """Deletes the products by given id"""
    product = await ProductsService().find_by_id(args.product_id)
    if not product:
        await request.abort(404, gettext("Product not found"))

    await ProductsService().delete(product)
    return Response({"success": True})
