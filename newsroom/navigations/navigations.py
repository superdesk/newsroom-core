from typing import List, Optional
import newsroom
from newsroom.products.products import get_products_by_company, get_products_by_user
import superdesk

from newsroom.utils import is_admin
from newsroom.types import Company, Navigation, UserData


class NavigationsResource(newsroom.Resource):
    """
    Navigations schema
    """

    schema = {
        "name": {"type": "string", "unique": True, "required": True},
        "description": {"type": "string"},
        "is_enabled": {"type": "boolean", "default": True},
        "order": {"type": "integer", "nullable": True},
        "product_type": {"type": "string", "default": "wire"},
        # list of images for tile based navigation
        "tile_images": {"type": "list", "nullable": True},
        "original_creator": newsroom.Resource.rel("users"),
        "version_creator": newsroom.Resource.rel("users"),
    }

    datasource = {"source": "navigations", "default_sort": [("order", 1), ("name", 1)]}
    item_methods = ["GET", "PATCH", "DELETE"]
    resource_methods = ["GET", "POST"]


class NavigationsService(newsroom.Service):
    def on_delete(self, doc):
        super().on_delete(doc)
        navigation = doc.get("_id")
        products = superdesk.get_resource_service("products").find(where={"navigations": navigation})
        for product in products:
            product["navigations"].remove(navigation)
            superdesk.get_resource_service("products").patch(product["_id"], product)


def get_navigations(user: Optional[UserData], company: Optional[Company], product_type="wire") -> List[Navigation]:
    """
    Returns list of navigations for given user and company
    """
    if user and is_admin(user):
        return list(superdesk.get_resource_service("navigations").get(req=None, lookup={"product_type": product_type}))

    products = []
    if company:
        products += get_products_by_company(company, None, product_type, True)
    if user:
        products += get_products_by_user(user, product_type, None)

    navigation_ids = []
    for p in products:
        if p.get("navigations"):
            navigation_ids.extend(p["navigations"])
    return get_navigations_by_ids(navigation_ids)


def get_navigations_by_company(company: Company, product_type="wire"):
    """
    Returns list of navigations for given company id
    Navigations will contain the list of product ids
    """
    return get_navigations(None, company, product_type)


def get_navigations_by_ids(navigation_ids):
    """
    Returns the list of navigations for navigation_ids
    """
    if not navigation_ids:
        return []

    return list(
        superdesk.get_resource_service("navigations").get(
            req=None, lookup={"_id": {"$in": navigation_ids}, "is_enabled": True}
        )
    )
