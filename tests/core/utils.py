from typing import Any
from superdesk import get_resource_service
from newsroom.core import get_current_wsgi_app


def add_company_products(app, company_id, products):
    company = app.data.find_one("companies", req=None, _id=company_id)
    app.data.insert("products", products)
    company_products = company["products"] or []

    for product in products:
        company_products.append({"_id": product["_id"], "section": product["product_type"], "seats": 0})

    app.data.update("companies", company["_id"], {"products": company_products}, company)


async def create_entries_for(resource: str, items: list[Any]):
    """
    Attemps create a new resource entries. First tries with async, otherwise it falls back to
    sync resources.
    """
    app = get_current_wsgi_app()
    async_app = app.async_app

    try:
        return await async_app.resources.get_resource_service(resource).create(items)
    except KeyError:
        ids = []
        for item in items:
            app.data.mongo._mongotize(item, resource)
            ids.extend(get_resource_service(resource).post([item]))
        return ids
