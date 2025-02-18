from bson.objectid import ObjectId
from typing import Annotated, Optional, List, Dict, Any

from superdesk.core.module import Module
from superdesk.core.resources.validators import validate_data_relation_async
from superdesk.core.resources import (
    ResourceConfig,
    MongoResourceConfig,
    RestEndpointConfig,
    RestParentLink,
)

from newsroom import MONGO_PREFIX
from newsroom.auth.utils import get_current_request
from newsroom.mgmt_api.products import CPProductsService
from newsroom.mgmt_api.companies import CPCompaniesService, company_resource_config
from newsroom.core.resources import NewshubResourceModel, NewshubAsyncResourceService
from newsroom.products.views import get_product_ref


class CompanyProductsResource(NewshubResourceModel):
    product: Annotated[Optional[str], validate_data_relation_async("products", convert_to_objectid=True)]
    seats: int = 0
    link: bool = False


async def get_company() -> Dict[str, Any]:
    request = get_current_request()
    company = await CPCompaniesService().find_by_id(ObjectId(request.get_view_args("companies")))
    return company.to_dict()


def get_company_products(company: Dict[str, Any]) -> List[dict]:
    return company.get("products") or []


class CompanyProductsService(NewshubAsyncResourceService[CompanyProductsResource]):
    async def on_create(self, docs: List[CompanyProductsResource], **kwargs):
        ids: List = []
        company = await get_company()

        for doc in docs:
            product_id = doc.product
            if not product_id:
                continue  # Skip if no product is provided

            link = doc.link
            product_data_cursor = await CPProductsService().find_by_id(ObjectId(product_id))
            if not product_data_cursor:
                continue

            product = product_data_cursor

            print(product, "\n\n\n\n\n\n\n\n\n")
            company_products = [p for p in get_company_products(company) if p["_id"] != product.id]

            if link:
                company_products.append(get_product_ref(product, doc.seats).to_dict())

            ids.append(product_id)
        if ids:
            await CPCompaniesService().update(ObjectId(company["_id"]), {"products": company_products})
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
    name="newsroom.mgmt_api.companies_products",
    resources=[company_products_resource_config],
)
