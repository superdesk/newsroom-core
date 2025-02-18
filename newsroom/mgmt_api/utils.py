import bson
import ipaddress
from typing import List, Dict, Optional, Any
from quart_babel import gettext

from superdesk.core.types import Response

from newsroom.types import CompanyProduct
from newsroom.products import ProductsService


async def validate_product_refs(product_refs: List[CompanyProduct]) -> List[Dict[Any, Any]]:
    products_service = ProductsService()
    product_refs = [ref.to_dict() if isinstance(ref, CompanyProduct) else ref for ref in product_refs]
    product_ids = [bson.ObjectId(ref["_id"]) for ref in product_refs]
    cursor = await products_service.search(lookup={"_id": {"$in": product_ids}})
    products = await cursor.to_list_raw()
    products_by_id = {str(product["_id"]): product for product in products}

    for ref in product_refs:
        product = products_by_id.get(str(ref["_id"]))
        assert product is not None
        ref["section"] = product["product_type"]
    return product_refs


def get_errors_company(updates: CompanyProduct, original: Optional[CompanyProduct] = None) -> Response:
    if original is None:
        original = CompanyProduct()  # Create a default empty CompanyProduct object if None

    updates_data = updates.to_dict()
    if not (updates_data.get("name") or original.get("name")):
        return Response({"name": gettext("Name not found")}, 400)

    if updates.allowed_ip_list:
        errors = []
        for ip in updates["allowed_ip_list"]:
            try:
                ipaddress.ip_network(ip, strict=True)
            except ValueError as e:
                errors.append(gettext("{0}: {1}".format(ip, e)))

        if errors:
            return Response({"allowed_ip_list": errors}, 400)
