from typing import Optional, List
from bson import ObjectId

from newsroom.types import Company


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
