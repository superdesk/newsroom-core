from typing import Optional, List
from bson import ObjectId

from newsroom.types import Company
from apps.prepopulate.app_initialize import get_filepath
from flask import json


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


def load_countries_list():
    with open(get_filepath("vocabularies.json")) as f:
        cvs = json.load(f)
    for cv in cvs:
        if cv["_id"] == "countries":
            return cv["items"]
    return []
