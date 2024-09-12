from bson import ObjectId
from newsroom.utils import is_admin
from newsroom.types import Company, Navigation, UserData
from newsroom.products.products import get_products_by_company, get_products_by_user

from .service import NavigationsService


async def get_navigations_as_list():
    """
    Returns a list of all navigations in raw mode
    """
    return [obj async for obj in NavigationsService().get_all_raw()]


async def get_navigations(user: UserData | None, company: Company | None, product_type="wire") -> list[Navigation]:
    """
    Returns list of navigations for given user and company
    """
    if user and is_admin(user):
        cursor = await NavigationsService().search(lookup={"product_type": product_type})
        return await cursor.to_list_raw()

    products = []
    if company:
        products += get_products_by_company(company, None, product_type, True)
    if user:
        products += get_products_by_user(user, product_type, None)

    navigation_ids = []
    for p in products:
        if p.get("navigations"):
            navigation_ids.extend(p["navigations"])
    return await get_navigations_by_ids(navigation_ids)


async def get_navigations_by_company(company: Company, product_type="wire") -> list[Navigation]:
    """
    Returns list of navigations for given company id
    Navigations will contain the list of product ids
    """
    return await get_navigations(None, company, product_type)


async def get_navigations_by_ids(navigation_ids: list[str | ObjectId]) -> list[Navigation]:
    """
    Returns the list of navigations for navigation_ids
    """
    if not navigation_ids:
        return []

    navigation_ids = [str(x) for x in navigation_ids]
    cursor = await NavigationsService().search(lookup={"_id": {"$in": navigation_ids}, "is_enabled": True})
    return await cursor.to_list_raw()
