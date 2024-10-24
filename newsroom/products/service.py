import warnings

from typing import Any, Sequence

from bson import ObjectId
from superdesk.core.resources import AsyncCacheableService

from newsroom.types import ProductResourceModel
from newsroom.companies.companies_async import CompanyService
from newsroom.core.resources.service import NewshubAsyncResourceService


class ProductsService(NewshubAsyncResourceService[ProductResourceModel], AsyncCacheableService):
    cache_lookup = {"is_enabled": True}

    async def create(self, docs: Sequence[ProductResourceModel | dict[str, Any]]) -> list[str]:
        company_products: dict[ObjectId, Any] = {}

        for doc in docs:
            if isinstance(doc, ProductResourceModel):
                doc = doc.to_dict()

            if doc.get("companies"):
                for company_id in doc["companies"]:
                    company_products.setdefault(company_id, []).append(doc)

        res = await super().create(docs)

        # TODO-ASYNC: check what is going on with this deprecation
        if company_products:
            warnings.warn("Using deprecated product.companies", DeprecationWarning)

        company_service = CompanyService()
        for company_id, products in company_products.items():
            company = await company_service.find_by_id(company_id)

            if company:
                updates = {
                    "products": company.products or [],
                }
                for product in products:
                    updates["products"].append({"_id": product["_id"], "section": product["product_type"], "seats": 0})
                await company_service.system_update(company.id, updates)

        return res

    async def on_deleted(self, doc: ProductResourceModel):
        from newsroom.users import UsersService
        from newsroom.companies.companies_async import CompanyService

        lookup = {"products._id": doc.id}

        for service in [UsersService(), CompanyService()]:
            search_cursor = await service.search(lookup)
            for item in await search_cursor.to_list_raw():
                updates = {"products": [p for p in item["products"] if str(p["_id"]) != str(doc.id)]}
                await service.system_update(item["_id"], updates)
