from typing import Any, Sequence

from bson import ObjectId

from superdesk.flask import g

from newsroom.types import (
    Company,
    Product,
    NavigationIds,
    ProductResourceModel,
    CompanyResource,
    SectionEnum,
    UserResourceModel,
)
from newsroom.auth.utils import get_company_from_request, get_user_or_none_from_request
from .service import ProductsService
from ..utils import any_objectid_in_list

IdsList = NavigationIds


async def get_products_by_company(
    company: Company | None,
    navigation_ids: NavigationIds | None = None,
    product_type: SectionEnum | None = None,
    unlimited_only: bool = False,
) -> list[Product]:
    """Get the list of products for a company

    :param company: Company
    :param navigation_ids: List of Navigation Ids
    :param product_type: Type of the product
    :param unlimited_only: Include unlimited only products
    """

    return [
        product.to_dict()
        for product in await get_products_by_company_async(
            CompanyResource.from_dict(company), navigation_ids, product_type, unlimited_only
        )
    ]


async def get_products_by_company_async(
    company: CompanyResource | None,
    navigation_ids: NavigationIds | None = None,
    product_type: SectionEnum | None = None,
    unlimited_only: bool = False,
) -> list[ProductResourceModel]:
    """Get the list of products for a company

    :param company: Company
    :param navigation_ids: List of Navigation Ids
    :param product_type: Type of the product
    :param unlimited_only: Include unlimited only products
    """
    if company is None:
        return []

    company_product_ids = [
        product._id
        for product in company.products or []
        if (product_type is None or product.section == product_type) and (not unlimited_only or not product.seats)
    ]

    if company_product_ids:
        lookup = get_products_lookup(company_product_ids, navigation_ids)
        cursor = await ProductsService().search(lookup)
        return await cursor.to_list()

    return []


async def get_products_by_user_async(
    user: UserResourceModel, section: SectionEnum, navigation_ids: NavigationIds | None
) -> list[ProductResourceModel]:
    ids = [p._id for p in user.products or [] if p.section == section]
    if ids:
        lookup = get_products_lookup(ids, navigation_ids)
        cursor = await ProductsService().search(lookup)
        return await cursor.to_list()

    return []


async def get_products_for_request_user_and_company(section: SectionEnum) -> list[ProductResourceModel]:
    cache_key = f"request_products_{section}"
    request_products: list[ProductResourceModel] | None = g.get(cache_key)
    if request_products is not None:
        return request_products

    product_ids: list[ObjectId] = []
    user = get_user_or_none_from_request(None)
    if user is not None:
        product_ids.extend([product._id for product in user.products or [] if product.section == section])

    company = get_company_from_request(None)
    if company is not None:
        product_ids.extend(
            [
                product._id
                for product in company.products or []
                if product.section == section and (user is None or not product.seats)
            ]
        )

    if len(product_ids):
        lookup = get_products_lookup(product_ids, None)
        cursor = await ProductsService().search(lookup)
        request_products = await cursor.to_list()
    else:
        request_products = []

    setattr(g, cache_key, request_products)
    return request_products


async def get_products_by_navigation_async(
    navigation_ids: NavigationIds, product_type: SectionEnum | None = None
) -> list[ProductResourceModel]:
    return [
        product
        async for product in ProductsService().get_all()
        if (
            any_objectid_in_list(navigation_ids, product.navigations or [])
            and (product_type is None or product.product_type == product_type)
        )
    ]


def get_products_lookup(
    product_ids: Sequence[str | ObjectId], navigation_ids: Sequence[str | ObjectId] | None
) -> dict[str, Any]:
    lookup = {"_id": {"$in": product_ids}}

    if navigation_ids:
        lookup["navigations"] = {"$in": navigation_ids}

    return lookup
