from typing import Any
from newsroom.types import Company, Product, NavigationIds
from newsroom.utils import parse_objectid
from .service import ProductsService


IdsList = NavigationIds


async def get_products_by_company(
    company: Company | None,
    navigation_ids: NavigationIds | None = None,
    product_type: str | None = None,
    unlimited_only: bool = False,
) -> list[Product]:
    """Get the list of products for a company

    :param company: Company
    :param navigation_ids: List of Navigation Ids
    :param product_type: Type of the product
    :param unlimited_only: Include unlimited only products
    """
    if company is None:
        return []

    company_product_ids = [
        parse_objectid(product["_id"])
        for product in company.get("products") or []
        if (product_type is None or product["section"] == product_type)
        and (not unlimited_only or not product.get("seats"))
    ]

    if company_product_ids:
        lookup = get_products_lookup(company_product_ids, navigation_ids)
        cursor = await ProductsService().search(lookup)
        return cursor.to_list_raw()

    return []


def get_products_lookup(product_ids: IdsList, navigation_ids: IdsList | None) -> dict[str, Any]:
    lookup = {"_id": {"$in": product_ids}}

    if navigation_ids:
        lookup["navigations"] = {"$in": navigation_ids}

    return lookup
