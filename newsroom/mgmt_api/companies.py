from bson.objectid import ObjectId

from newsroom.products.views import get_product_ref
from newsroom.utils import find_one
from superdesk.errors import SuperdeskApiError
from superdesk.core.resources import ResourceConfig, MongoResourceConfig, RestEndpointConfig, RestParentLink
from content_api import MONGO_PREFIX
from typing import Annotated, Optional, List
from newsroom.types import CompanyResource
from newsroom.companies.companies_async import CompanyService
from .utils import validate_product_refs, get_errors_company
from newsroom.core import get_current_wsgi_app
from superdesk.core.resources.validators import validate_data_relation_async
from newsroom.core.resources import NewshubResourceModel
from newsroom.core.resources import NewshubAsyncResourceService
from superdesk.core.types import Request, Response
from superdesk.core.module import Module


class CPCompaniesResource(CompanyResource):
    """
    CP Companies Schema
    """

    country: Optional[str] = None


class CPCompaniesService(CompanyService):
    async def on_create(self, docs: List[CompanyResource]):
        await super().on_create(docs)
        for doc in docs:
            errors = get_errors_company(doc)
            if errors:
                message = "invalid ip address"
                raise SuperdeskApiError.badRequestError(message=message, payload=message)
            if doc.get("products"):
                await validate_product_refs(doc["products"])

    async def on_created(self, docs):
        await super().on_created(docs)
        app = get_current_wsgi_app()
        for doc in docs:
            await app.cache.set(str(doc["_id"]), doc)

    async def on_update(self, updates, original):
        if updates.get("products"):
            await validate_product_refs(updates["products"])
        await super().on_update(updates, original)
        app = get_current_wsgi_app()
        await app.cache.delete(str(original["_id"]))

    async def on_delete(self, doc):
        await super().on_deleted(doc)
        app = get_current_wsgi_app()
        await app.cache.delete(str(doc["_id"]))


company_resource_config = ResourceConfig(
    name="companies",
    data_class=CPCompaniesResource,
    service=CPCompaniesService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
)


class CompanyProductsResource(NewshubResourceModel):
    product: Annotated[ObjectId, validate_data_relation_async("products")]
    seats: int = 0
    link: bool = False


async def get_company(request: Request):
    company = await find_one("companies", _id=ObjectId(request.get_view_args("companies")))
    return company


async def get_company_products(company):
    return company.get("products") or []


class CompanyProductsService(NewshubAsyncResourceService[CompanyProductsResource]):
    async def get(self, req, lookup):
        self.company = await get_company(req)
        company_products = await get_company_products(self.company)
        lookup["_id"] = {"$in": [p["_id"] for p in company_products]}
        lookup.pop("companies", None)
        return await super().get(req, lookup)

    async def find_one(self, req, **lookup):
        lookup.pop("companies", None)
        return await super().find_one(req, **lookup)

    async def on_create(self, docs, **kwargs):
        ids = []
        for doc in docs:
            id = doc.pop("product")
            link = doc.pop("link")
            product = await find_one("products", _id=ObjectId(id))
            company = await get_company()
            assert product
            company_products = [p for p in await get_company_products(company) if p["_id"] != product["_id"]]
            if link:
                company_products.append(get_product_ref(product, doc.get("seats")))
            await self.system_update(company["_id"], {"products": company_products}, company)
            ids.append(id)
        return ids

    async def on_fetched(self, doc):
        for item in doc["_items"]:
            await self._fix_link(item)
            if hasattr(self, "company") and self.company and self.company.get("products"):
                for product_ref in self.company["products"]:
                    if product_ref["_id"] == item["_id"]:
                        item["seats"] = product_ref["seats"]
                        break
        return await super().on_fetched(doc)

    async def on_fetched_item(self, doc):
        await self._fix_link(doc)
        return await super().on_fetched_item(doc)

    async def _fix_link(self, item):
        company_id = request.view_args["companies"]
        item["_links"]["self"]["href"] = f"companies/{company_id}/products/{item['_id']}"


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
        resource_methods=["GET", "POST"],
    ),
)

module = Module(
    name="newsroom.mgmt_api.companies",
    resources=[company_products_resource_config, company_resource_config],
)
