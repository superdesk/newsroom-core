import warnings

from typing import List, Optional, Union
from bson import ObjectId

import newsroom
import superdesk
from superdesk.services import CacheableService

from newsroom.types import Company, Product, User, NavigationIds, PRODUCT_TYPES
from newsroom.utils import any_objectid_in_list, parse_objectid

IdsList = NavigationIds


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
        "product_type": {"type": "string", "default": "wire", "allowed": PRODUCT_TYPES},
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

    def on_deleted(self, doc: Product) -> None:
        lookup = {"products._id": doc["_id"]}
        for resource in ("users", "companies"):
            items = superdesk.get_resource_service(resource).get(req=None, lookup=lookup)
            for item in items:
                updates = {"products": [p for p in item["products"] if p["_id"] != doc["_id"]]}
                superdesk.get_resource_service(resource).system_update(item["_id"], updates, item)

    def create(self, docs):
        company_products = {}
        for doc in docs:
            if doc.get("companies"):
                for company_id in doc["companies"]:
                    company_products.setdefault(company_id, []).append(doc)
        res = super().create(docs)
        if company_products:
            warnings.warn("Using deprecated product.companies", DeprecationWarning)

        company_service = superdesk.get_resource_service("companies")
        for company_id, products in company_products.items():
            company = company_service.find_one(req=None, _id=company_id)
            if company:
                updates = {
                    "products": company.get("products") or [],
                }
                for product in products:
                    updates["products"].append({"_id": product["_id"], "section": product["product_type"], "seats": 0})
                company_service.system_update(company["_id"], updates, company)
        return res


products_service = ProductsService()


def get_products_by_navigation(navigation_ids: NavigationIds, product_type: Optional[str] = None) -> List[Product]:
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
    if not product:
        return None

    if company_id is not None and parse_objectid(company_id) not in product.get("companies") or []:
        return None

    if product_type is not None and product.get("product_type") != product_type:
        return None

    return product


def get_products_by_company(
    company: Optional[Company],
    navigation_ids: Optional[NavigationIds] = None,
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

    company_product_ids = [
        parse_objectid(product["_id"])
        for product in company.get("products") or []
        if (product_type is None or product["section"] == product_type)
        and (not unlimited_only or not product.get("seats"))
    ]

    if company_product_ids:
        lookup = get_products_lookup(company_product_ids, navigation_ids)
        return list(products_service.get_from_mongo(req=None, lookup=lookup))

    return []


def get_products_by_user(user: User, section: str, navigation_ids: Optional[NavigationIds]) -> List[Product]:
    if user.get("products"):
        ids = [parse_objectid(p["_id"]) for p in user["products"] if p["section"] == section]
        if ids:
            lookup = get_products_lookup(ids, navigation_ids)
            return list(products_service.get_from_mongo(req=None, lookup=lookup))

    return []


def get_products_lookup(product_ids: IdsList, navigation_ids: Optional[IdsList]):
    lookup = {"_id": {"$in": product_ids}}

    if navigation_ids:
        lookup["navigations"] = {"$in": navigation_ids}

    return lookup
