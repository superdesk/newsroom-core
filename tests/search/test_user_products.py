import pytest
import tests.utils as utils

from newsroom.users.users import UserRole

from .fixtures import (
    USERS,
    COMPANIES,
    PRODUCTS,
)


@pytest.fixture(autouse=True)
def init(app):
    app.data.insert("users", USERS)
    app.data.insert("companies", COMPANIES)
    app.data.insert("products", PRODUCTS)


def test_user_products(app, client):
    product = {"name": "test", "query": "headline:somethingthatdoesnotexist", "is_enabled": True}
    app.data.insert("products", [product])

    manager = USERS[-1].copy()
    manager["email"] = "manager@example.com"
    manager["user_type"] = UserRole.ACCOUNT_MANAGEMENT.value
    manager.pop("_id")

    app.data.insert("users", [manager])

    utils.login(client, manager)

    data = utils.get_json(client, "/wire/search")
    assert 1 >= len(data["_items"])

    utils.patch_json(
        client,
        f"/api/users/{manager['_id']}",
        {
            "products": [{"section": "wire", "_id": product["_id"]}],
        },
    )

    data = utils.get_json(client, "/wire/search")
    assert 0 == len(data["_items"])

    app.data.update("products", product["_id"], {"query": "headline:WEATHER"}, product)

    data = utils.get_json(client, "/wire/search")
    assert 1 >= len(data["_items"])

    with pytest.raises(AssertionError) as err:
        utils.patch_json(client, f"/api/users/{USERS[0]['_id']}", {"products": []})
    assert "403" in str(err)

    with pytest.raises(AssertionError) as err:
        utils.delete_json(client, f"/api/users/{USERS[0]['_id']}", {})
    assert "403" in str(err)
