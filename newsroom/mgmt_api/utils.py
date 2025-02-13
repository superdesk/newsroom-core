import bson
from superdesk.core.types import Response
from quart_babel import gettext
import ipaddress
from newsroom.products import ProductsService


async def validate_product_refs(product_refs):
    products_service = ProductsService()
    product_ids = [bson.ObjectId(ref["_id"]) for ref in product_refs]
    products = list(await products_service.search(lookup={"_id": {"$in": product_ids}}))
    products_by_id = {str(product["_id"]): product for product in products}

    for ref in product_refs:
        product = products_by_id.get(str(ref["_id"]))
        assert product is not None
        ref["section"] = product["product_type"]


def get_errors_company(updates, original=None):
    if original is None:
        original = {}

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
