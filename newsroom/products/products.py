from typing import Any, Dict, List, Optional
from bson import ObjectId

import newsroom
import superdesk

from newsroom.types import Company, Product


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


class ProductsService(newsroom.Service):
    def on_deleted(self, doc):
        lookup = {"products._id": doc["_id"]}
        for resource in ("users", "companies"):
            items = superdesk.get_resource_service(resource).get(req=None, lookup=lookup)
            for item in items:
                updates = {"products": [p for p in item["products"] if p["_id"] != doc["_id"]]}
                superdesk.get_resource_service(resource).system_update(item["_id"], updates, item)


def _get_navigation_query(ids):
    return {"$in": [ObjectId(oid) for oid in ids]} if type(ids) is list else ObjectId(ids)


def get_products_by_navigation(navigation_id, product_type=None):
    lookup = {"is_enabled": True, "navigations": _get_navigation_query(navigation_id)}

    if product_type is not None:
        lookup["product_type"] = product_type

    return list(superdesk.get_resource_service("products").get(req=None, lookup=lookup))


def get_product_by_id(product_id, product_type=None, company_id=None):
    lookup = {"_id": ObjectId(product_id), "is_enabled": True}

    if company_id is not None:
        lookup["companies"] = ObjectId(company_id)

    if product_type is not None:
        lookup["product_type"] = product_type

    return list(superdesk.get_resource_service("products").get(req=None, lookup=lookup))


def get_products_by_company(
    company: Optional[Company], navigation_id=None, product_type=None, unlimited_only=False
) -> List[Product]:
    """Get the list of products for a company

    :param company_id: Company Id
    :param navigation_id: Navigation Id
    :param product_type: Type of the product
    """
    if company is None:
        return []
    lookup: Dict[str, Any] = {"is_enabled": True}
    if "products" in company:
        product_ids = []
        if company.get("products"):
            product_ids = [
                ObjectId(p["_id"])
                for p in company["products"]
                if p["section"] == product_type and (not unlimited_only or not p.get("seats"))
            ]
        if product_ids:
            lookup["_id"] = {"$in": product_ids}
        else:
            # no products selected for a company
            return []
    else:
        lookup["companies"] = ObjectId(company["_id"])
    if navigation_id:
        lookup["navigations"] = _get_navigation_query(navigation_id)
    if product_type:
        lookup["product_type"] = product_type

    products = list(superdesk.get_resource_service("products").get(req=None, lookup=lookup))
    return products


def get_products_dict_by_company(company_id):
    lookup = {"is_enabled": True, "companies": ObjectId(company_id)}
    return list(superdesk.get_resource_service("products").get(req=None, lookup=lookup))


def get_products_by_user(user, section):
    if user.get("products"):
        ids = [p["_id"] for p in user["products"] if p["section"] == section]
        if ids:
            lookup = {"is_enabled": True, "_id": {"$in": ids}}
            return list(superdesk.get_resource_service("products").get(req=None, lookup=lookup))
    return []
