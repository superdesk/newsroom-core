from typing import List, Optional, Dict, Any

from superdesk.core.module import Module
from superdesk.errors import SuperdeskApiError
from superdesk.core.resources import MongoResourceConfig, ResourceConfig, RestEndpointConfig

from newsroom import MONGO_PREFIX
from newsroom.types import CompanyResource
from newsroom.companies.companies_async import CompanyService
from newsroom.core import get_current_wsgi_app
from .utils import validate_product_refs, get_errors_company


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

    async def on_update(self, updates: Dict[str, Any], original: CompanyResource):
        if updates.get("products"):
            updates["products"] = await validate_product_refs(updates["products"])
        await super().on_update(updates, original)
        app = get_current_wsgi_app()
        app.cache.delete(str(original.id))

    async def on_delete(self, doc: CompanyResource):
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

module = Module(
    name="newsroom.mgmt_api.companies",
    resources=[company_resource_config],
)
