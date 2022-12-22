from flask import url_for
from pytest import fixture

from .fixtures import (
    TEST_USER_ID,
    USERS,
    COMPANIES,
    PRODUCTS,
)


@fixture(autouse=True)
def init(app):
    app.data.insert("users", USERS)
    app.data.insert("companies", COMPANIES)
    app.data.insert("products", PRODUCTS)


def test_user_products(app, client):
    product = {"name": "test", "query": "headline:BAR", "is_enabled": True}
    app.data.insert("products", [product])

    user = app.data.find_one("users", req=None, _id=TEST_USER_ID)
    updates = {"products": [{"section": "wire", "_id": product["_id"]}]}
    app.data.update("users", user["_id"], updates, user)

    client.post(
        url_for("auth.login"),
        data={
            "email": user["email"],
            "password": "admin",
        },
    )

    resp = client.get("/wire/search")
    assert resp.status_code == 200
    data = resp.json
    assert 0 == len(data["_items"])

    app.data.update("products", product["_id"], {"query": "headline:WEATHER"}, product)

    resp = client.get("/wire/search")
    assert resp.status_code == 200
    data = resp.json
    assert 1 == len(data["_items"])
