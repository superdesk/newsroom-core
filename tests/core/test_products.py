import importlib

from bson import ObjectId
from flask import json
from pytest import fixture

from newsroom.tests.users import test_login_succeeds_for_admin

from .. import utils


@fixture(autouse=True)
def product(app):
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
def companies(app):
    _companies = [
        {"name": "test1", "sections": {"wire": True}},
        {"name": "test2"},
        {"name": "test3"},
    ]

    app.data.insert("companies", _companies)
    return _companies


def test_product_list_fails_for_anonymous_user(client, anonymous_user):
    response = client.get("/products/search")
    assert response.status_code == 403
    assert b"Forbidden" in response.data


def test_return_search_for_products(client):
    test_login_succeeds_for_admin(client)
    client.post(
        "/products/new",
        data=json.dumps(
            {
                "name": "Breaking",
                "description": "Breaking news",
                "is_enabled": True,
                "sd_product_id": "123",
            }
        ),
        content_type="application/json",
    )

    response = client.get("/products/search?q=br")
    assert "Breaking" in response.get_data(as_text=True)


def test_create_fails_in_validation(client):
    test_login_succeeds_for_admin(client)
    response = client.post(
        "/products/new",
        data=json.dumps(
            {
                "description": "Breaking news",
                "is_enabled": True,
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "name" in response.get_data(as_text=True)


def test_update_products(client):
    test_login_succeeds_for_admin(client)

    resp = client.post(
        "/products/59b4c5c61d41c8d736852fbf",
        data=json.dumps(
            {
                "name": "Sport",
                "description": "foo",
                "is_enabled": True,
                "sd_product_id": "123",
            }
        ),
        content_type="application/json",
    )

    assert 200 == resp.status_code

    response = client.get("/products")
    assert "foo" in response.get_data(as_text=True)


def test_delete_product(client):
    test_login_succeeds_for_admin(client)

    client.post(
        "/products/new",
        data=json.dumps(
            {
                "name": "Breaking",
                "description": "Breaking news",
                "parents": "59b4c5c61d41c8d736852fbf",
                "is_enabled": True,
                "query": "bar",
            }
        ),
        content_type="application/json",
    )

    resp = client.delete("/products/59b4c5c61d41c8d736852fbf")
    assert 200 == resp.status_code

    response = client.get("/products")
    data = json.loads(response.get_data())
    assert 1 == len(data)
    assert data[0]["name"] == "Breaking"


def test_gets_all_products(client, app):
    test_login_succeeds_for_admin(client)

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

    resp = client.get("/products")
    data = json.loads(resp.get_data())
    assert 251 == len(data)


def test_assign_products_to_companies(client, app, product, companies):
    test_login_succeeds_for_admin(client)
    assign_product_to_companies(client, product, companies)

    company = app.data.find_one("companies", req=None, _id=companies[0]["_id"])
    assert "products" in company
    assert company["products"] == [{"section": "wire", "_id": product["_id"], "seats": 0}]

    resp = client.post(
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


def test_products_company_migration(app, companies):
    app.data.insert("products", [{"name": "test1", "companies": [companies[0]["_id"], str(companies[1]["_id"])]}])

    update_module = importlib.import_module("data_updates.00009_20230116-145407_products")
    data_update = update_module.DataUpdate()

    db = app.data.pymongo("products").db
    data_update.forwards(db[data_update.resource], db)

    company = app.data.find_one("companies", req=None, _id=companies[0]["_id"])
    assert 1 == len(company["products"])


def test_delete_assigned_product(client, app, product, companies, user):
    product2 = {
        "name": "test",
        "is_enabled": True,
    }

    app.data.insert("products", [product2])

    assign_product_to_companies(client, product, companies)
    assign_product_to_companies(client, product2, companies)
    assign_product_to_user(client, product2, user)

    company = app.data.find_one("companies", req=None, _id=companies[0]["_id"])
    assert 2 == len(company["products"])

    updated_user = app.data.find_one("users", req=None, _id=user["_id"])
    assert 1 == len(updated_user["products"])

    utils.delete_json(client, f"/products/{product2['_id']}")

    company = app.data.find_one("companies", req=None, _id=companies[0]["_id"])
    assert 1 == len(company["products"])
    assert product2["_id"] not in [p["_id"] for p in company["products"]]

    updated_user = app.data.find_one("users", req=None, _id=user["_id"])
    assert 0 == len(updated_user["products"])


def test_company_and_user_products(client, app, public_company, public_user, product):
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
            {"headline": "finance item", "type": "text"},
            {"headline": "sports item", "type": "text"},
        ],
    )

    assign_product_to_companies(client, product, [public_company])

    # this is noop, user can only get products assigned to company
    assign_product_to_user(client, product2, public_user)

    utils.login(client, public_user)

    resp = client.get("/wire/search")
    assert 200 == resp.status_code
    assert 1 == len(resp.json["_items"]), resp.json["_items"]


def assign_product_to_companies(client, product, companies):
    resp = client.post(
        "/products/{}/companies".format(product["_id"]),
        json={
            "companies": [company["_id"] for company in companies],
        },
    )

    assert resp.status_code == 200


def assign_product_to_user(client, product, user):
    products = user.get("products") or []
    products.append({"_id": product["_id"], "section": product.get("product_type", "wire")})
    utils.patch_json(client, f"/api/_users/{user['_id']}", {"products": products, "sections": {"wire": True}})
