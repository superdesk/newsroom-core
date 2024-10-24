from typing import List, Dict, Any
from copy import deepcopy

from newsroom.types import CompanyResource
from newsroom.core.resources import NewshubAsyncResourceService
from newsroom.signals import company_create
from newsroom.auth.utils import is_from_request, get_current_request, get_company_from_request
from newsroom.types.company import CompanyProduct

from ..utils import get_company_section_names, get_company_product_ids, get_users_by_company


class CompanyService(NewshubAsyncResourceService[CompanyResource]):
    resource_name = "companies"
    clear_item_cache_on_update = True

    async def on_create(self, docs: List[CompanyResource]) -> None:
        await super().on_create(docs)
        for company in docs:
            company_create.send(self, company=company.to_dict())

    def _get_products(self, updates: Dict[str, Any], original: CompanyResource):
        """
        Loop over products and checks if any of them is instance of CompanyProduct to
        convert them into dict
        """
        for product in updates.get("products", original.products) or []:
            if isinstance(product, CompanyProduct):
                yield product.to_dict()
            else:
                yield product

    async def on_update(self, updates: Dict[str, Any], original: CompanyResource) -> None:
        await super().on_update(updates, original)
        if "sections" in updates or "products" in updates:
            sections = updates.get("sections", original.sections) or {}
            updates["products"] = [
                product
                for product in self._get_products(updates, original)
                if product.get("section") and sections.get(product["section"]) is True
            ]

    async def on_updated(self, updates: Dict[str, Any], original: CompanyResource) -> None:
        from newsroom.users.service import UsersService

        await super().on_updated(updates, original)

        if is_from_request():
            # If this is from a request, test to see if we need to update the
            # current company cached in request storage
            current_request = get_current_request()
            current_company = get_company_from_request(current_request)
            if current_company and current_company.id == original.id:
                updated = original.to_dict()
                updated.update(updates)
                updated_company = CompanyResource.from_dict(updated)
                current_request.storage.request.set("company_instance", updated_company)

        original_dict = original.to_dict()
        updated = deepcopy(original_dict)
        updated.update(updates)

        original_section_names = get_company_section_names(original_dict)
        original_product_ids = get_company_product_ids(original_dict)

        updated_section_names = get_company_section_names(updated)
        updated_product_ids = get_company_product_ids(updated)

        if original_section_names != updated_section_names or original_product_ids != updated_product_ids:
            company_users = await get_users_by_company(original.id)
            async for user in company_users:
                user_updates = {
                    "sections": (
                        {}
                        if not user.sections
                        else {section: user.sections.get(section, False) for section in updated_section_names}
                    ),
                    "products": [
                        product
                        for product in user.products or []
                        if product.section.value in updated_section_names and product._id in updated_product_ids
                    ],
                }

                await UsersService().update(user.id, updates=user_updates)
