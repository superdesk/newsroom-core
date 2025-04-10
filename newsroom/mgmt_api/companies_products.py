from bson.objectid import ObjectId
from typing import List, Optional
from pydantic import BaseModel

from newsroom.types.common import SectionEnum
from newsroom.products import ProductsService
from newsroom.products.views import get_product_ref
from newsroom.mgmt_api.companies import CPCompaniesService
from newsroom.types import CompanyResource, CompanyProduct

from superdesk.core.module import Module
from superdesk.core.types import Request, Response
from superdesk.core.resources import fields
from superdesk.core.web import EndpointGroup


def get_company_products(company: CompanyResource) -> List[CompanyProduct]:
    return company.products or []


company_products_endpoints = EndpointGroup("company_products", __name__)


class CPCompanyProduct(CompanyProduct):
    # Declare section as optional
    section: Optional[SectionEnum] = None  # type: ignore

    @classmethod
    def from_dict(cls, data: dict):
        """Allow `product` key as an alias for `_id`"""
        if "product" in data:
            data["_id"] = data.pop("product")
        return super().from_dict(data)


class CompanyProductRouteArguments(BaseModel):
    company_id: fields.ObjectId

    async def get_company(self) -> CompanyResource | None:
        return await CompanyResource.get_service().find_by_id(self.company_id)


@company_products_endpoints.endpoint("companies/<regex('[a-f0-9]{24}'):company_id>/products", methods=["POST"])
async def update_company_products(args: CompanyProductRouteArguments, params: None, request: Request) -> Response:
    company = await args.get_company()
    if not company:
        return Response({"error": "Company not found"}, status=404)

    product_links_json = await request.get_json()
    product_links: list[CPCompanyProduct] = [CPCompanyProduct.from_dict(link) for link in product_links_json]
    ids: List = []

    company_products = get_company_products(company)
    updated_products = company_products[:]

    for doc in product_links:
        product_id = doc._id
        if not product_id:
            continue

        product_data = await ProductsService().find_by_id(ObjectId(product_id))
        if not product_data:
            continue

        updated_products = [p for p in updated_products if p._id != product_data.id]

        if doc.link:
            updated_products.append(get_product_ref(product_data, doc.seats).to_dict())

        ids.append(product_id)

    if ids:
        await CPCompaniesService().system_update(ObjectId(company.id), {"products": updated_products})

    return Response({"updated_product_ids": ids}, 201)


@company_products_endpoints.endpoint("companies/<regex('[a-f0-9]{24}'):company_id>/products", methods=["GET"])
async def get_company_products_endpoint(args: CompanyProductRouteArguments, params: None, request: Request) -> Response:
    company = await args.get_company()
    if not company:
        return Response({"error": "Company not found"}, status=404)

    company_products = get_company_products(company)

    products_data = []
    for product in company_products:
        product_data = await ProductsService().find_by_id(ObjectId(product._id))
        if product_data:
            item = {
                "name": product_data.name,
                "description": product_data.description,
                "query": product_data.query,
                "product_type": product_data.product_type,
                "seats": product.seats or 0,
                "_links": {"self": {"href": f"/companies/{company.id}/products/{product._id}"}},
            }
            products_data.append(item)

    return Response({"_items": products_data}, 200)


module = Module(
    name="newsroom.mgmt_api.companies_products",
    endpoints=[company_products_endpoints],
)
