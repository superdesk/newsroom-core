from typing import Any
from bson import ObjectId
from superdesk import get_resource_service
from newsroom.core import get_current_wsgi_app


async def find_one_by_id(resource: str, item_id: ObjectId | str) -> Any | None:
    """
    Attempts to create a new resource entries. First tries with async, otherwise it falls back to
    sync resources.
    """
    app = get_current_wsgi_app()
    async_app = app.async_app

    try:
        model_instance = await async_app.resources.get_resource_service(resource).find_by_id(item_id)
        return model_instance.to_dict(context={"use_objectid": True}) if model_instance else None
    except KeyError:
        return app.data.find_one(resource, req=None, _id=item_id)


async def find_one_for(resource: str, **kwargs: Any) -> Any | None:
    app = get_current_wsgi_app()
    async_app = app.async_app

    try:
        model_instance = await async_app.resources.get_resource_service(resource).find_one(**kwargs)
        return model_instance.to_dict(context={"use_objectid": True}) if model_instance else None
    except KeyError:
        return app.data.find_one(resource, req=None, **kwargs)


async def get_all(resource: str) -> list[Any]:
    app = get_current_wsgi_app()
    async_app = app.async_app

    try:
        return [
            # item.to_dict(context={"use_objectid": True})
            item
            async for item in async_app.resources.get_resource_service(resource).get_all_raw()
        ]
    except KeyError:
        return [item for item in app.data.find(resource, {})]


async def add_company_products(app, company_id, products):
    company = await find_one_by_id("companies", company_id)
    await create_entries_for("products", products)
    company_products = company["products"] or []

    for product in products:
        company_products.append({"_id": product["_id"], "section": product["product_type"], "seats": 0})

    await update_entries_for("companies", company["_id"], {"products": company_products}, company)


async def create_entries_for(resource: str, items: list[Any]) -> list[ObjectId | str]:
    """
    Attempts to create a new resource entries. First tries with async, otherwise it falls back to
    sync resources.
    """
    app = get_current_wsgi_app()
    async_app = app.async_app

    try:
        return await async_app.resources.get_resource_service(resource).create(items)
    except KeyError:
        print(f"Failed to find async service for {resource}")
        ids = []
        for item in items:
            app.data.mongo._mongotize(item, resource)
            ids.extend(get_resource_service(resource).post([item]))
        return ids


async def update_entries_for(resource: str, item_id: str | ObjectId, updates: dict[str, Any], original: Any):
    """
    Attempts to update existing resource entries. First tries with async, otherwise it falls back to
    sync resources.
    """
    app = get_current_wsgi_app()
    async_app = app.async_app

    try:
        await async_app.resources.get_resource_service(resource).update(item_id, updates)
    except KeyError:
        app.data.update(resource, item_id, updates, original)


async def delete_entries_for(resource: str) -> None:
    """
    Attempts to remove all items from the resources MongoDB and/or Elastic.
    First tries with async, otherwise it falls back to sync resources.
    """

    app = get_current_wsgi_app()
    async_app = app.async_app

    try:
        await async_app.resources.get_resource_service(resource).delete_many({})
    except KeyError:
        app.data.remove(resource)
