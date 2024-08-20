from typing import TYPE_CHECKING, Dict, List, Optional, Union

from bson import ObjectId
from superdesk.core.resources.cursor import ResourceCursorAsync

from newsroom.types import Company
from newsroom.utils import query_resource

from .companies_async.types import CompanyProduct, CompanyResource

# avoid circular reference as it's used for type hints only
if TYPE_CHECKING:
    from newsroom.users.model import UserResourceModel


def restrict_coverage_info(company: Optional[Company]) -> bool:
    if company:
        return company.get("restrict_coverage_info", False)
    return False


def get_company_section_names(company: Company) -> List[str]:
    sections = company.get("sections") or {}
    return sorted([section for section, enabled in sections.items() if enabled])


def get_company_product_ids(company: Company) -> List[Optional[ObjectId]]:
    return sorted(
        [
            product.get("_id")
            for product in company.get("products") or []
            if product.get("section") and (company.get("sections") or {}).get(product["section"]) is True
        ],
        key=lambda o: str(o),
    )


def get_updated_sections(updates, original, company: Optional[CompanyResource]) -> Dict[str, bool]:
    sections: Dict[str, bool] = {}
    if "sections" in updates:
        sections = updates["sections"] or {}
    elif "sections" in original:
        sections = original["sections"] or {}

    if not company:
        return sections

    company_section_names = get_company_section_names(company.model_dump(by_alias=True))
    return {section: enabled and section in company_section_names for section, enabled in sections.items()}


def get_updated_products(updates, original, company: Optional[CompanyResource]) -> List[CompanyProduct]:
    products: List[CompanyProduct] = []
    if "products" in updates:
        products = updates["products"] or []
    elif "products" in original:
        products = original["products"] or []

    if not company:
        return products

    company_dict = company.model_dump(by_alias=True)
    company_section_names = get_company_section_names(company_dict)
    company_product_ids = get_company_product_ids(company_dict)

    return [
        product
        for product in products
        if product.section in company_section_names and product._id in company_product_ids
    ]


def get_companies_id_by_product(product_id: str) -> List[str]:
    """
    Get company IDs based on product ID.

    Parameters:
        product_id (str): The ID of the product.

    Returns:
        List[str]: A list of company IDs associated with the specified product.
    """
    companies = list(query_resource("companies"))
    return [
        str(company["_id"])
        for company in companies
        if any(prod["_id"] == ObjectId(product_id) for prod in company.get("products", []))
    ]


async def get_users_by_company(company_id: Union[str, ObjectId]) -> ResourceCursorAsync["UserResourceModel"]:
    """
    Get all the users for the given company ID.

    Parameters:
        company_id (str | ObjectId): The ID of the company

    Returns:
        ResourceCursorAsync[UserResourceModel]: A result cursor of users that belong to the given company (if any)
    """

    from newsroom.users.service import UsersService

    return await UsersService().search(lookup={"company": ObjectId(company_id)})
