from typing import Any
from newsroom.core import get_current_wsgi_app
from motor.motor_asyncio import AsyncIOMotorCollection


def add_company_products(app, company_id, products):
    company = app.data.find_one("companies", req=None, _id=company_id)
    app.data.insert("products", products)
    company_products = company["products"] or []

    for product in products:
        company_products.append({"_id": product["_id"], "section": product["product_type"], "seats": 0})

    app.data.update("companies", company["_id"], {"products": company_products}, company)


def get_db_collection(collection_name: str) -> AsyncIOMotorCollection:
    """
    Retrieve an asynchronous MongoDB collection.

    Args:
        collection_name (str): The name of the MongoDB collection.

    Returns:
        AsyncIOMotorCollection: The asynchronous MongoDB collection object.
    """
    async_app = get_current_wsgi_app().async_app
    return async_app.mongo.get_collection_async(collection_name)


async def insert_into(collection_name: str, data: list[Any]):
    """
    Insert multiple documents into a specified MongoDB collection asynchronously.

    Args:
        collection_name (str): The name of the MongoDB collection.
        data (list[Any]): A list of documents to insert into the collection.
    """
    db_collection = get_db_collection(collection_name)
    await db_collection.insert_many(data)
