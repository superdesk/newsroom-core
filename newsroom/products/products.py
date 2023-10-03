from typing import List, Optional, Union
from bson import ObjectId

import newsroom
import superdesk
from superdesk.services import CacheableService

from newsroom.types import Company, Product, User
from newsroom.utils import any_objectid_in_list


class ProductsResource(newsroom.Resource):
    """
    Products schema
    """

    schema = {
        "name": {"type": "string", "unique": True, "required": True},
        "description": {"type": "string"},
        "sd_product_id": {"type": "string"},
        "query": {"type": "string"},
        "planning_item_query": {"type": "string"},
        "is_enabled": {"type": "boolean", "default": True},
        "navigations": {
            "type": "list",
            "schema": newsroom.Resource.rel("navigations", nullable=True),
        },
        "companies": {  # obsolete
            "type": "list",
            "schema": newsroom.Resource.rel("companies"),
            "nullable": True,
        },
        "product_type": {"type": "string", "default": "wire"},
        "original_creator": newsroom.Resource.rel("users"),
        "version_creator": newsroom.Resource.rel("users"),
    }
    datasource = {"source": "products", "default_sort": [("name", 1)]}
    item_methods = ["GET", "PATCH", "DELETE"]
    resource_methods = ["GET", "POST"]
    query_objectid_as_string = True  # needed for companies/navigations lookup to work
    internal_resource = True


class ProductsService(CacheableService):
    cache_lookup = {"is_enabled": True}

    def on_deleted(self, doc):
        lookup = {"products._id": doc["_id"]}
        for resource in ("users", "companies"):
            items = superdesk.get_resource_service(resource).get(req=None, lookup=lookup)
            for item in items:
                updates = {"products": [p for p in item["products"] if p["_id"] != doc["_id"]]}
                superdesk.get_resource_service(resource).system_update(item["_id"], updates, item)


products_service = ProductsService()


def get_products_by_navigation(
    navigation_ids: List[Union[str, ObjectId]], product_type: Optional[str] = None
) -> List[Product]:
    return [
        product
        for product in products_service.get_cached()
        if (
            any_objectid_in_list(navigation_ids, product.get("navigations") or [])
            and (product_type is None or product.get("product_type") == product_type)
        )
    ]


def get_product_by_id(
    product_id: Union[str, ObjectId], product_type: Optional[str] = None, company_id: Optional[ObjectId] = None
) -> Optional[Product]:
    product = products_service.get_cached_by_id(product_id)

    if company_id is not None and ObjectId(company_id) not in product.get("companies") or []:
        return None

    if product_type is not None and product.get("product_type") != product_type:
        return None

    return product


def get_products_by_company(
    company: Optional[Company],
    navigation_ids: Optional[List[Union[str, ObjectId]]] = None,
    product_type: Optional[str] = None,
    unlimited_only: Optional[bool] = False,
) -> List[Product]:
    """Get the list of products for a company

    :param company: Company
    :param navigation_ids: List of Navigation Ids
    :param product_type: Type of the product
    :param unlimited_only: Include unlimited only products
    """

    if company is None:
        return []

    company_id = ObjectId(company["_id"])
    company_product_ids = [
        ObjectId(product["_id"])
        for product in company.get("products") or []
        if product["section"] == product_type and (not unlimited_only or not product.get("seats"))
    ]

    if "products" in company and not company_product_ids:
        # no products selected for this company
        return []

    def product_matches(product: Product):
        if "products" in (company or {}) and product["_id"] not in company_product_ids:
            return False
        elif "products" not in (company or {}) and company_id not in (product.get("companies") or []):
            return False
        elif product_type and product.get("product_type") != product_type:
            return False
        elif navigation_ids and not any_objectid_in_list(navigation_ids, product.get("navigations") or []):
            return False

        return True

    return [product for product in products_service.get_cached() if product_matches(product)]


def get_products_by_user(user: User, section: str) -> List[Product]:
    if user.get("products"):
        ids = [p["_id"] for p in user["products"] if p["section"] == section]
        if ids:
            return [product for product in products_service.get_cached() if product["_id"] in ids]
    return []
