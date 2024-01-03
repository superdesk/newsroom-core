import pytest
import superdesk
import tests.utils as utils

from flask import g
from newsroom.users.users import UserRole

from .fixtures import (
    USERS,
    COMPANIES,
    PRODUCTS,
    PUBLIC_USER_ID,
)


@pytest.fixture(autouse=True)
def init(app):
    app.data.insert("users", USERS)
    app.data.insert("companies", COMPANIES)
    app.data.insert("products", PRODUCTS)


@pytest.fixture
def product(app):
    product = {
        "name": "test",
        "query": "headline:somethingthatdoesnotexist",
        "is_enabled": True,
        "product_type": "wire",
    }
    app.data.insert("products", [product])
    return product


@pytest.fixture
def company(app, product):
    company = COMPANIES[1].copy()
    company["name"] = "Example co."
    company["products"] = [
        {
            "_id": product["_id"],
            "section": product["product_type"],
        }
    ]
    company.pop("_id")
    app.data.insert("companies", [company])
    return company


@pytest.fixture
def manager(app, client, product, company):
    manager = USERS[1].copy()
    manager["company"] = company["_id"]
    manager["email"] = "manager@example.com"
    manager["user_type"] = UserRole.COMPANY_ADMIN.value
    manager.pop("_id")

    app.data.insert("users", [manager])

    utils.login(client, manager)

    data = utils.get_json(client, "/wire/search")
    assert 0 < len(data["_items"])

    return manager


def test_user_products(app, client, manager, product, company):
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

    data = utils.get_json(client, "/wire/search?q=weather")
    assert 0 == len(data["_items"])

    app.data.update("products", product["_id"], {"query": "headline:WEATHER"}, product)
    g.pop("cached:products", None)

    data = utils.get_json(client, "/wire/search")
    assert 1 == len(data["_items"])

    data = utils.get_json(client, "/wire/search?q=amazon")
    assert 0 == len(data["_items"])


def test_user_products_after_company_update(app, client, manager, product, company):
    superdesk.get_resource_service("companies").patch(
        company["_id"],
        {
            "products": [{"section": "wire", "_id": product["_id"]}],
        },
    )

    user = app.data.find_one("users", req=None, _id=manager["_id"])
    assert user["products"]


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

    # has section but no products
    with pytest.raises(AssertionError) as err:
        utils.get_json(client, "/agenda/search")
    assert "403" in str(err)

    utils.patch_json(
        client, f"/api/_users/{manager['_id']}", {"products": [{"section": "agenda", "_id": product["_id"]}]}
    )

    # works now with company product
    data = utils.get_json(client, "/agenda/search")
    assert data

    # section not enabled
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
    assert "401" in str(err)

    with pytest.raises(AssertionError) as err:
        utils.delete_json(client, f"/api/_users/{USERS[0]['_id']}", {})
    assert "401" in str(err)

    with pytest.raises(AssertionError) as err:
        utils.patch_json(client, f"/api/_users/{USERS[1]['_id']}", {"company": COMPANIES[0]["_id"]})
    assert "401" in str(err)


def test_public_user_can_edit_his_dashboard(client, manager):
    public_user = next((user for user in USERS if user["_id"] == PUBLIC_USER_ID))
    utils.login(client, public_user)
    utils.patch_json(client, f"/api/_users/{PUBLIC_USER_ID}", {"dashboards": []})
