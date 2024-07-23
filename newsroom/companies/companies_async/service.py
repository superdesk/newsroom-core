from typing import List, Dict, Any
from copy import deepcopy

from superdesk import get_resource_service

from newsroom.core.resources import NewshubAsyncResourceService
from newsroom.signals import company_create

from ..utils import get_company_section_names, get_company_product_ids
from .types import CompanyResource


class CompanyService(NewshubAsyncResourceService[CompanyResource]):
    resource_name = "companies"
    clear_item_cache_on_update = True

    async def on_create(self, docs: List[CompanyResource]) -> None:
        await super().on_create(docs)
        for company in docs:
            company_create.send(self, company=company.model_dump(by_alias=True, exclude_unset=True))

    async def on_update(self, updates: Dict[str, Any], original: CompanyResource) -> None:
        await super().on_update(updates, original)
        if "sections" in updates or "products" in updates:
            sections = updates.get("sections", original.get("sections")) or {}
            updates["products"] = [
                product
                for product in updates.get("products", original.get("products")) or []
                if product.get("section") and sections.get(product["section"]) is True
            ]

    async def on_updated(self, updates: Dict[str, Any], original: CompanyResource) -> None:
        await super().on_updated(updates, original)

        original_dict = original.model_dump(by_alias=True, exclude_unset=True)
        updated = deepcopy(original_dict)
        updated.update(updates)

        original_section_names = get_company_section_names(original_dict)
        original_product_ids = get_company_product_ids(original_dict)

        updated_section_names = get_company_section_names(updated)
        updated_product_ids = get_company_product_ids(updated)

        if original_section_names != updated_section_names or original_product_ids != updated_product_ids:
            # TODO-ASYNC: Replace this with async users
            user_service = get_resource_service("users")
            for user in user_service.get(req=None, lookup={"company": original.id}):
                user_updates = {
                    "sections": (
                        {}
                        if not user.get("sections")
                        else {
                            section: (user.get("sections") or {}).get(section, False)
                            for section in updated_section_names
                        }
                    ),
                    "products": [
                        product
                        for product in user.get("products") or []
                        if product.get("section") in updated_section_names and product.get("_id") in updated_product_ids
                    ],
                }
                user_service.patch(user["_id"], updates=user_updates)
