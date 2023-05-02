from flask import g
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


@pytest.fixture
def product(app):
    product = {"name": "test", "query": "headline:somethingthatdoesnotexist", "is_enabled": True}
    app.data.insert("products", [product])
    return product


@pytest.fixture
def manager(app, client):
    manager = USERS[1].copy()
    manager["email"] = "manager@example.com"
    manager["user_type"] = UserRole.COMPANY_ADMIN.value
    manager.pop("_id")

    app.data.insert("users", [manager])

    utils.login(client, manager)

    data = utils.get_json(client, "/wire/search")
    assert 0 < len(data["_items"])

    return manager


def test_user_products(app, client, manager, product):
    g.settings["allow_companies_to_manage_products"]["value"] = True
    utils.patch_json(
        client,
        f"/api/_users/{manager['_id']}",
        {
            "products": [{"section": "wire", "_id": product["_id"]}],
        },
    )

    data = utils.get_json(client, "/wire/search")
    assert 0 == len(data["_items"])

    app.data.update("products", product["_id"], {"query": "headline:WEATHER"}, product)

    data = utils.get_json(client, "/wire/search")
    assert 1 >= len(data["_items"])


def test_user_sections(app, client, manager, product):
    g.settings["allow_companies_to_manage_products"]["value"] = True
    utils.patch_json(
        client,
        f"/api/_users/{manager['_id']}",
        {
            "sections": {"wire": True, "agenda": False},
        },
    )

    with pytest.raises(AssertionError) as err:
        utils.get_json(client, "/agenda/search")
    assert "403" in str(err)

    utils.patch_json(
        client,
        f"/api/_users/{manager['_id']}",
        {
            "sections": {"agenda": True},
        },
    )

    with pytest.raises(AssertionError) as err:
        utils.get_json(client, "/agenda/search")
    assert "403" in str(err)

    utils.patch_json(
        client, f"/api/_users/{manager['_id']}", {"products": [{"section": "agenda", "_id": product["_id"]}]}
    )

    data = utils.get_json(client, "/agenda/search")
    assert data

    with pytest.raises(AssertionError) as err:
        utils.get_json(client, "/wire/search")
    assert "403" in str(err)

    utils.patch_json(
        client,
        f"/api/_users/{manager['_id']}",
        {
            "sections": None,
        },
    )

    data = utils.get_json(client, "/agenda/search")
    assert data

    company = app.data.find_one("companies", req=None, _id=manager["company"])
    assert company
    app.data.update("companies", manager["company"], {"sections": {"agenda": True}}, company)

    with pytest.raises(AssertionError) as err:
        utils.get_json(client, "/wire/search")
    assert "403" in str(err)

    data = utils.get_json(client, "/agenda/search")
    assert data


def test_other_company_user_changes_blocked(client, manager):
    with pytest.raises(AssertionError) as err:
        utils.patch_json(client, f"/api/_users/{USERS[0]['_id']}", {"products": []})
    assert "403" in str(err)

    with pytest.raises(AssertionError) as err:
        utils.delete_json(client, f"/api/_users/{USERS[0]['_id']}", {})
    assert "403" in str(err)

    with pytest.raises(AssertionError) as err:
        utils.patch_json(client, f"/api/_users/{USERS[1]['_id']}", {"company": COMPANIES[0]["_id"]})
    assert "403" in str(err)
