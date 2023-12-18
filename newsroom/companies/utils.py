from typing import Optional, List
from bson import ObjectId

from newsroom.types import Company

from newsroom.utils import query_resource


def restrict_coverage_info(company: Optional[Company]) -> bool:
    if company:
        return company.get("restrict_coverage_info", False)
    return False


def get_company_section_names(company: Company) -> List[str]:
    return sorted([section for section, enabled in company.get("sections", {}).items() if enabled])


def get_company_product_ids(company: Company) -> List[ObjectId]:
    return sorted(
        [
            product.get("_id")
            for product in company.get("products", [])
            if product.get("section") and (company.get("sections") or {}).get(product["section"]) is True
        ],
        key=lambda o: str(o),
    )


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
