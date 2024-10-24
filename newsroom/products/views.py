import re
from typing import Any, Tuple, cast

from bson import ObjectId, errors
from pydantic import BaseModel
from quart_babel import gettext

from superdesk.core.web import EndpointGroup
from superdesk.core.types import Request, Response

from newsroom.auth import auth_rules
from newsroom.core import get_current_wsgi_app
from newsroom.types import Product, ProductRef
from newsroom.utils import get_json_or_400_async
from newsroom.products.service import ProductsService
from newsroom.navigations import get_navigations_as_list
from newsroom.companies.companies_async import CompanyService
from newsroom.types.company import CompanyProduct, CompanyResource

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


async def convert_ids_or_abort(request: Request, data: dict[str, Any], key: str):
    try:
        if key in data:
            data[key] = [ObjectId(str_id) for str_id in data[key]]
    except errors.InvalidId:
        await request.abort(400, f"Please provide valid {key} ids")


@products_endpoints.endpoint("/products/new", methods=["POST"], auth=[auth_rules.admin_only])
async def create(request: Request):
    creation_data = await get_json_or_400_async(request)

    # convert navigations and companies ids from string to ObjectId
    for key in ["companies", "navigations"]:
        await convert_ids_or_abort(request, creation_data, key)

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


async def update_company_products(
    company: CompanyResource, product_id: ObjectId, selected_companies: list[ObjectId], product_ref: ProductRef
) -> Tuple[list[ProductRef], bool]:
    """
    Updates the company's product list by either adding or removing a product reference.

    Returns:
        Tuple[List[ProductRef], bool]: A tuple where the first element is the of company products,
        and the second element is a boolean indicating whether an update is required.
    """

    if company.id in selected_companies:
        return add_product_to_company(company, product_id, product_ref)
    else:
        return remove_product_from_company(company, product_id)


def add_product_to_company(
    company: CompanyResource, product_id: ObjectId, product_ref: ProductRef
) -> Tuple[list[ProductRef], bool]:
    """
    Adds a product to the company's product list if it doesn't already exist.
    """
    if not product_in_company(company, product_id):
        company_products: list[ProductRef] = (cast(list[ProductRef], company.products)).copy()
        company_products.append(product_ref)
        return company_products, True
    return cast(list[ProductRef], company.products), False


def product_in_company(company: CompanyResource, product_id: ObjectId) -> bool:
    """
    Checks if a product is already in a given Company products list.
    """
    for product in company.products:
        if str(product._id) == str(product_id):
            return True
    return False


def remove_product_from_company(company: CompanyResource, product_id: ObjectId) -> Tuple[list[ProductRef], bool]:
    """
    Removes a product from the company's product list if it exists.

    Returns:
        A tuple with the list of products of the company and a boolean to indicate if an update is
        required or not.
    """
    company_products = [p for p in company.products if str(p._id) != str(product_id)]
    is_update_required = len(company_products) != len(company.products)

    return cast(list[ProductRef], company_products), is_update_required


def update_company_sections(company: CompanyResource, company_products: list[ProductRef]):
    sections = company.sections
    for product in company_products:
        if isinstance(product, CompanyProduct):
            product = product.to_dict()
        sections.setdefault(product["section"], True)
    return sections


@products_endpoints.endpoint(
    "/products/<string:product_id>/companies", methods=["POST"], auth=[auth_rules.account_manager_only]
)
async def update_companies(args: ProductsArgs, _p: None, request: Request):
    product = await ProductsService().find_by_id(args.product_id)
    if not product:
        await request.abort(404, gettext("Product not found"))

    updates = await request.get_json()
    await convert_ids_or_abort(request, updates, "companies")
    selected_companies: list[ObjectId] = updates.get("companies") or []
    product_ref = get_product_ref(product.to_dict())

    async for company in CompanyService().get_all():
        company_products, update_required = await update_company_products(
            company, ObjectId(args.product_id), selected_companies, product_ref
        )

        if update_required:
            company_sections = update_company_sections(company, company_products)
            await CompanyService().update(company.id, {"products": company_products, "sections": company_sections})

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
