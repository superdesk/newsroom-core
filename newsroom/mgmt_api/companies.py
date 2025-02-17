from bson.objectid import ObjectId

from superdesk.errors import SuperdeskApiError
from superdesk.core.resources import ResourceConfig, MongoResourceConfig, RestEndpointConfig, RestParentLink
from content_api import MONGO_PREFIX
from typing import Annotated, Optional, List
from newsroom.types import CompanyResource, CompanyProduct
from newsroom.companies.companies_async import CompanyService
from .utils import validate_product_refs, get_errors_company
from newsroom.core import get_current_wsgi_app
from superdesk.core.resources.validators import validate_data_relation_async
from newsroom.core.resources import NewshubResourceModel
from newsroom.core.resources import NewshubAsyncResourceService
from superdesk.core.module import Module
from newsroom.mgmt_api.products import CPProductsService
from newsroom.auth.utils import get_current_request


class CPCompaniesResource(CompanyResource):
    """
    CP Companies Schema
    """

    country: Optional[str] = "CAN"


class CPCompaniesService(CompanyService):
    async def on_create(self, docs: List[CPCompaniesResource]):
        for doc in docs:
            errors = get_errors_company(doc)
            if errors:
                message = "invalid ip address"
                raise SuperdeskApiError.badRequestError(message=message, payload=message)
            if doc.products:
                doc.products = await validate_product_refs(doc.products)
        await super().on_create(docs)

    async def on_created(self, docs: List[CPCompaniesResource]):
        await super().on_created(docs)
        app = get_current_wsgi_app()
        for doc in docs:
            app.cache.set(str(doc.id), doc)

    async def on_update(self, updates, original):
        if updates.get("products"):
            updates["products"] = await validate_product_refs(updates["products"])
        await super().on_update(updates, original)
        app = get_current_wsgi_app()
        app.cache.delete(str(original.id))

    async def on_delete(self, doc):
        await super().on_deleted(doc)
        app = get_current_wsgi_app()
        app.cache.delete(str(doc.id))


company_resource_config = ResourceConfig(
    name="companies",
    data_class=CPCompaniesResource,
    service=CPCompaniesService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    rest_endpoints=RestEndpointConfig(auth=False),
)


class CompanyProductsResource(NewshubResourceModel):
    product: Annotated[Optional[str], validate_data_relation_async("products", convert_to_objectid=True)]
    seats: int = 0
    link: bool = False


async def get_company():
    request = get_current_request()
    company = await CPCompaniesService().find_by_id(ObjectId(request.get_view_args("companies")))
    return company.to_dict()


def get_company_products(company):
    return company.get("products") or []


def get_product_ref(product, seats) -> CompanyProduct:
    return CompanyProduct(
        _id=product.get("_id"),
        section=product.get("product_type"),
        seats=seats,
    )


class CompanyProductsService(NewshubAsyncResourceService[CompanyProductsResource]):
    async def on_create(self, docs, **kwargs):
        ids = []
        company = await get_company()  # Fetch company once instead of inside the loop

        for doc in docs:
            product_id = doc.product
            if not product_id:
                continue  # Skip if no product is provided

            link = doc.link
            product_data_cursor = await CPProductsService().find_by_id(ObjectId(product_id))
            if not product_data_cursor:
                continue  # Skip if product is not found

            product = product_data_cursor.to_dict()
            company_products = [p for p in get_company_products(company) if p["_id"] != product["_id"]]

            if link:
                company_products.append(get_product_ref(product, doc.seats).to_dict())

        if ids:
            await CPCompaniesService().system_update(ObjectId(company["_id"]), {"products": company_products})

        ids.append(product_id)
        return ids


company_products_resource_config = ResourceConfig(
    name="company_products",
    data_class=CompanyProductsResource,
    service=CompanyProductsService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    rest_endpoints=RestEndpointConfig(
        parent_links=[
            RestParentLink(
                resource_name=company_resource_config.name,
                model_id_field="companies",
            ),
        ],
        url="products",
        auth=False,
    ),
)

module = Module(
    name="newsroom.mgmt_api.companies",
    resources=[company_products_resource_config, company_resource_config],
)
