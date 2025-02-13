from bson.objectid import ObjectId

from newsroom.products.views import get_product_ref
from newsroom.utils import find_one
from superdesk.errors import SuperdeskApiError
from superdesk.core.resources import ResourceConfig, MongoResourceConfig, RestEndpointConfig, RestParentLink
from content_api import MONGO_PREFIX
from typing import Annotated, Optional, List, Union
from newsroom.types import CompanyResource
from newsroom.companies.companies_async import CompanyService
from .utils import validate_product_refs, get_errors_company
from newsroom.core import get_current_wsgi_app
from superdesk.core.resources.validators import validate_data_relation_async
from newsroom.core.resources import NewshubResourceModel
from newsroom.core.resources import NewshubAsyncResourceService
from superdesk.core.types import Request, Response
from superdesk.core.module import Module
from newsroom.mgmt_api.products import CPProductsService
from newsroom.auth.utils import get_current_request


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
            if doc.products:
                await validate_product_refs(doc.products)

    async def on_created(self, docs):
        await super().on_created(docs)
        app = get_current_wsgi_app()
        for doc in docs:
            app.cache.set(str(doc.id), doc)

    async def on_update(self, updates, original):
        if updates.get("products"):
            await validate_product_refs(updates.products)
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
    product: Annotated[Optional[ObjectId], validate_data_relation_async("products")]
    seats: int = 0
    link: bool = False


async def get_company():
    request = get_current_request()
    company = await CompanyService().find_by_id(ObjectId(request.get_view_args("companies")))
    return company.to_dict()


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
            doc = doc.to_dict()
            if isinstance(doc.get("product"), str):
                doc["product"] = ObjectId(doc["product"])
            id = doc.pop("product", None)
            if id:
                data = await CPProductsService().find_by_id(ObjectId(id))
                product = data.to_dict()
                company = await get_company()
                assert product
                company_products = [p for p in await get_company_products(company) if p["_id"] != product["_id"]]
                await CompanyService().system_update(company["_id"], {"products": company_products})
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
        from newsroom.auth.utils import get_current_request

        request = get_current_request()
        company_id = request.view_args["companies"]
        item["_links"]["self"]["href"] = f"companies/{company_id}/products/{item['_id']}"


from typing import Optional
from enum import Enum
from pydantic import BaseModel


class UserActions(str, Enum):
    activate = "activate"
    disable = "disable"


class RouteArguments(BaseModel):
    user_id: str
    action: UserActions


class URLParams(BaseModel):
    verbose: bool = False


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
