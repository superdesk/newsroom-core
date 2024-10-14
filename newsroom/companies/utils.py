from typing import TYPE_CHECKING, Optional, Union

from bson import ObjectId
from superdesk.flask import g
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


def get_company_section_names(company: Company) -> list[str]:
    sections = company.get("sections") or {}
    return sorted([section for section, enabled in sections.items() if enabled])


def get_company_product_ids(company: Company) -> list[Optional[ObjectId]]:
    return sorted(
        [
            ObjectId(product.get("_id"))
            for product in company.get("products") or []
            if product.get("section") and (company.get("sections") or {}).get(product["section"]) is True
        ],
        key=lambda o: str(o),
    )


def get_updated_sections(updates, original, company: Optional[CompanyResource]) -> dict[str, bool]:
    sections: dict[str, bool] = {}
    if "sections" in updates:
        sections = updates["sections"] or {}
    elif "sections" in original:
        sections = original["sections"] or {}

    if not company:
        return sections

    company_section_names = get_company_section_names(company.to_dict())
    return {section: enabled and section in company_section_names for section, enabled in sections.items()}


def get_updated_products(updates, original, company: Optional[CompanyResource]) -> list[CompanyProduct]:
    products: list[CompanyProduct] = []
    if "products" in updates:
        products = updates["products"] or []
    elif "products" in original:
        products = original["products"] or []

    if not company:
        return products

    company_dict = company.to_dict()
    company_section_names = get_company_section_names(company_dict)
    company_product_ids = get_company_product_ids(company_dict)

    return [
        product
        for product in products
        if product.section in company_section_names and product._id in company_product_ids
    ]


def get_companies_id_by_product(product_id: str) -> list[str]:
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


async def get_company(user: Optional["UserResourceModel"] = None, required=False) -> Optional[Company]:
    """
    Asynchronously retrieves the company associated with the given user or current session.

    Parameters:
    - user (User, optional): A dictionary containing user information. If not provided,
      the function attempts to retrieve the current user asynchronously.
    - required (bool, optional): If True, raises an error if no user is found. Default is False.

    Returns:
    - Optional[Company]: A dictionary representation of the Company if found, otherwise None.
    """
    from newsroom.users.utils import get_user_async, get_company_from_user
    from .companies_async.service import CompanyService

    company = None

    if user is None:
        user = await get_user_async(required=required)

    if user and user.company:
        company = await get_company_from_user(user)

    if not company and hasattr(g, "company_id"):  # if there is no user this might be company session (in news api)
        company = await CompanyService().find_by_id(g.company_id)

    if company:
        return company.to_dict()

    return None
