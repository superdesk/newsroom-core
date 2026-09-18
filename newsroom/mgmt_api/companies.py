from superdesk.core.module import Module
from superdesk.core.resources import MongoResourceConfig, ResourceConfig, RestEndpointConfig

from newsroom import MONGO_PREFIX
from newsroom.types import CompanyResource
from newsroom.companies.companies_async import CompanyService
from .utils import validate_product_refs


class CPCompaniesService(CompanyService):
    async def on_create(self, docs: list[CompanyResource]):
        for doc in docs:
            if doc.products:
                doc.products = await validate_product_refs(doc.products)
            if not doc.country:
                doc.country = "CAN"
        await super().on_create(docs)

    async def on_update(self, updates: dict, original: CompanyResource):
        if updates.get("products"):
            updates["products"] = await validate_product_refs(updates["products"])
        await super().on_update(updates, original)


company_resource_config = ResourceConfig(
    name="companies",
    data_class=CompanyResource,
    service=CPCompaniesService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    rest_endpoints=RestEndpointConfig(),
)

module = Module(
    name="newsroom.mgmt_api.companies",
    resources=[company_resource_config],
)
