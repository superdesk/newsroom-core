import importlib

from bson import ObjectId
from quart import json
from pytest import fixture

from newsroom.tests.users import test_login_succeeds_for_admin
from datetime import datetime

from .. import utils


@fixture(autouse=True)
async def product(app):
    _product = {
        "_id": ObjectId("59b4c5c61d41c8d736852fbf"),
        "name": "Sport",
        "description": "Top level sport product",
        "is_enabled": True,
        "query": "sports",
        "product_type": "wire",
    }
    app.data.insert("products", [_product])
    return _product


@fixture
async def companies(app):
    _companies = [
        {"name": "test1", "sections": {"wire": True}},
        {"name": "test2"},
        {"name": "test3"},
    ]

    app.data.insert("companies", _companies)
    return _companies


async def test_product_list_fails_for_anonymous_user(client, anonymous_user, public_user, app):
    async with app.test_request_context("/products/search"):
        await utils.logout(client)
        response = await client.get("/products/search")
        assert response.status_code == 302
        assert response.headers.get("location") == "/login"

        await utils.login(client, public_user)
        response = await client.get("/products/search", follow_redirects=True)
        assert response.status_code == 403, await response.get_data(as_text=True)
        assert b"Forbidden" in await response.get_data()


async def test_return_search_for_products(client):
    await test_login_succeeds_for_admin(client)
    await client.post(
        "/products/new",
        json={
            "name": "Breaking",
            "description": "Breaking news",
            "is_enabled": True,
            "sd_product_id": "123",
        },
    )

    response = await client.get("/products/search?q=br")
    assert "Breaking" in await response.get_data(as_text=True)


async def test_create_fails_in_validation(client):
    await test_login_succeeds_for_admin(client)
    response = await client.post(
        "/products/new",
        json={
            "description": "Breaking news",
            "is_enabled": True,
        },
    )

    assert response.status_code == 400
    assert "name" in await response.get_data(as_text=True)


async def test_update_products(client):
    await test_login_succeeds_for_admin(client)

    resp = await client.post(
        "/products/59b4c5c61d41c8d736852fbf",
        json={
            "name": "Sport",
            "description": "foo",
            "is_enabled": True,
            "sd_product_id": "123",
        },
    )

    assert 200 == resp.status_code

    response = await client.get("/products")
    assert "foo" in await response.get_data(as_text=True)


async def test_delete_product(client):
    await test_login_succeeds_for_admin(client)

    await client.post(
        "/products/new",
        json={
            "name": "Breaking",
            "description": "Breaking news",
            "parents": "59b4c5c61d41c8d736852fbf",
            "is_enabled": True,
            "query": "bar",
        },
    )

    resp = await client.delete("/products/59b4c5c61d41c8d736852fbf")
    assert 200 == resp.status_code

    response = await client.get("/products")
    data = json.loads(await response.get_data())
    assert 1 == len(data)
    assert data[0]["name"] == "Breaking"


async def test_gets_all_products(client, app):
    await test_login_succeeds_for_admin(client)

    for i in range(250):
        app.data.insert(
            "products",
            [
                {
                    "name": "Sport-%s" % i,
                    "description": "Top level sport product",
                    "is_enabled": True,
                }
            ],
        )

    resp = await client.get("/products")
    data = json.loads(await resp.get_data())
    assert 251 == len(data)


async def test_assign_products_to_companies(client, app, product, companies):
    await test_login_succeeds_for_admin(client)
    await assign_product_to_companies(client, product, companies)

    company = app.data.find_one("companies", req=None, _id=companies[0]["_id"])
    assert "products" in company
    assert company["products"] == [{"section": "wire", "_id": product["_id"], "seats": 0}]

    resp = await client.post(
        "/products/{}/companies".format(product["_id"]),
        json={
            "companies": [
                companies[1]["_id"],
            ]
        },
    )

    assert 200 == resp.status_code

    company = app.data.find_one("companies", req=None, _id=companies[0]["_id"])
    assert company["products"] == []


async def test_products_company_migration(app, companies):
    product = {"name": "test1"}
    app.data.insert("products", [product])
    app.data.update("products", product["_id"], {"companies": [companies[0]["_id"], str(companies[1]["_id"])]}, product)

    update_module = importlib.import_module("data_updates.00009_20230116-145407_products")
    data_update = update_module.DataUpdate()

    db = app.data.pymongo("products").db
    data_update.forwards(db[data_update.resource], db)

    company = app.data.find_one("companies", req=None, _id=companies[0]["_id"])
    assert 1 == len(company["products"])


async def test_delete_assigned_product(client, app, product, companies, user):
    product2 = {
        "name": "test",
        "is_enabled": True,
    }

    app.data.insert("products", [product2])

    await utils.login(client, user)

    await assign_product_to_companies(client, product, companies)
    await assign_product_to_companies(client, product2, companies)
    await assign_product_to_user(client, product2, user)

    company = app.data.find_one("companies", req=None, _id=companies[0]["_id"])
    assert 2 == len(company["products"])

    updated_user = app.data.find_one("users", req=None, _id=user["_id"])
    assert 1 == len(updated_user["products"])

    await utils.delete_json(client, f"/products/{product2['_id']}")

    company = app.data.find_one("companies", req=None, _id=companies[0]["_id"])
    assert 1 == len(company["products"])
    assert product2["_id"] not in [p["_id"] for p in company["products"]]

    updated_user = app.data.find_one("users", req=None, _id=user["_id"])
    assert 0 == len(updated_user["products"])


async def test_company_and_user_products(client, app, public_company, public_user, product, admin):
    product2 = {
        "name": "test",
        "is_enabled": True,
        "query": "finance",
        "product_type": "wire",
    }

    app.data.insert("products", [product2])
    app.data.insert(
        "items",
        [
            {"headline": "finance item", "type": "text", "versioncreated": datetime.utcnow()},
            {"headline": "sports item", "type": "text", "versioncreated": datetime.utcnow()},
        ],
    )

    await assign_product_to_companies(client, product, [public_company])

    # this is noop, user can only get products assigned to company
    await utils.login(client, admin)
    await assign_product_to_user(client, product2, public_user)

    await utils.login(client, public_user)

    resp = await client.get("/wire/search")
    assert 200 == resp.status_code
    resp_json = await resp.get_json()
    assert 1 == len(resp_json["_items"]), resp_json["_items"]


async def assign_product_to_companies(client, product, companies):
    resp = await client.post(
        "/products/{}/companies".format(product["_id"]),
        json={
            "companies": [company["_id"] for company in companies],
        },
    )

    assert resp.status_code == 200


async def assign_product_to_user(client, product, user):
    products = user.get("products") or []
    products.append({"_id": product["_id"], "section": product.get("product_type", "wire")})
    await utils.patch_json(client, f"/api/_users/{user['_id']}", {"products": products, "sections": {"wire": True}})
