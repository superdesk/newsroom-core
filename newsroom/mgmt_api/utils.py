import bson

from typing import List
from newsroom.types import CompanyProduct
from newsroom.products import ProductsService


async def validate_product_refs(product_refs: List[CompanyProduct]) -> List[CompanyProduct]:
    products_service = ProductsService()
    product_refs = [ref.to_dict() if isinstance(ref, CompanyProduct) else ref for ref in product_refs]
    product_ids = [bson.ObjectId(ref["_id"]) for ref in product_refs]
    cursor = await products_service.search(lookup={"_id": {"$in": product_ids}})
    products = await cursor.to_list_raw()
    products_by_id = {str(product["_id"]): product for product in products}

    for ref in product_refs:
        product = products_by_id.get(str(ref["_id"]))
        if not product:
            raise ValueError(f"product {ref['_id']} not found")
        ref["section"] = product["product_type"]

    return product_refs
