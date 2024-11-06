import pytest
import superdesk
import tests.utils as utils

from quart import g
from newsroom.users.users import UserRole
from tests.core.utils import create_entries_for, update_entries_for, find_one_by_id

from .fixtures import (
    USERS,
    COMPANIES,
    PRODUCTS,
    PUBLIC_USER_ID,
)


@pytest.fixture(autouse=True)
async def init(app):
    await create_entries_for("companies", COMPANIES)
    await create_entries_for("users", USERS)
    await create_entries_for("products", PRODUCTS)


@pytest.fixture
async def product(app):
    product = {
        "name": "test",
        "query": "headline:somethingthatdoesnotexist",
        "is_enabled": True,
        "product_type": "wire",
    }
    await create_entries_for("products", [product])
    return product


@pytest.fixture
async def company(app, product):
    company = COMPANIES[1].copy()
    company["name"] = "Example co."
    company["products"] = [
        {
            "_id": product["_id"],
            "section": product["product_type"],
        }
    ]
    company.pop("_id")
    await create_entries_for("companies", [company])
    return company


@pytest.fixture
async def manager(app, client, product, company):
    manager = USERS[1].copy()
    manager["company"] = company["_id"]
    manager["email"] = "manager@example.com"
    manager["user_type"] = UserRole.COMPANY_ADMIN.value
    manager.pop("_id")

    await create_entries_for("auth_user", [manager])

    manager.pop("password")
    await utils.login(client, manager)

    data = await utils.get_json(client, "/wire/search")
    assert 0 < len(data["_items"])

    return manager


async def test_user_products(app, client, manager, product, company):
    g.settings["allow_companies_to_manage_products"]["value"] = True
    await utils.patch_json(
        client,
        f"/api/_users/{manager['_id']}",
        {
            "products": [{"section": "wire", "_id": product["_id"]}],
        },
    )

    data = await utils.get_json(client, "/wire/search")
    assert 0 == len(data["_items"])

    data = await utils.get_json(client, "/wire/search?q=weather")
    assert 0 == len(data["_items"])

    await update_entries_for("products", product["_id"], {"query": "headline:WEATHER"}, product)
    g.pop("cached:products", None)

    data = await utils.get_json(client, "/wire/search")
    assert 1 == len(data["_items"])

    data = await utils.get_json(client, "/wire/search?q=amazon")
    assert 0 == len(data["_items"])


async def test_user_products_after_company_update(app, client, manager, product, company):
    superdesk.get_resource_service("companies").patch(
        company["_id"],
        {
            "products": [{"section": "wire", "_id": product["_id"]}],
        },
    )

    user = await find_one_by_id("users", manager["_id"])
    assert user["products"]


async def test_user_sections(app, client, manager, product):
    g.settings["allow_companies_to_manage_products"]["value"] = True
    await utils.patch_json(
        client,
        f"/api/_users/{manager['_id']}",
        {
            "sections": {"wire": True, "agenda": False},
        },
    )

    with pytest.raises(AssertionError) as err:
        await utils.get_json(client, "/agenda/search")
    assert "403" in str(err)

    await utils.patch_json(
        client,
        f"/api/_users/{manager['_id']}",
        {
            "sections": {"agenda": True},
        },
    )

    # has section but no products
    with pytest.raises(AssertionError) as err:
        await utils.get_json(client, "/agenda/search")
        assert "403" in str(err)

    await utils.patch_json(
        client, f"/api/_users/{manager['_id']}", {"products": [{"section": "agenda", "_id": product["_id"]}]}
    )

    # works now with company product
    data = utils.get_json(client, "/agenda/search")
    assert data

    # section not enabled
    with pytest.raises(AssertionError) as err:
        await utils.get_json(client, "/wire/search")
    assert "403" in str(err)

    await utils.patch_json(
        client,
        f"/api/_users/{manager['_id']}",
        {
            "sections": None,
        },
    )

    data = utils.get_json(client, "/agenda/search")
    assert data

    company = await find_one_by_id("companies", manager["company"])
    assert company
    await update_entries_for("companies", manager["company"], {"sections": {"agenda": True}}, company)

    with pytest.raises(AssertionError) as err:
        await utils.get_json(client, "/wire/search")
    assert "403" in str(err)

    data = await utils.get_json(client, "/agenda/search")
    assert data


async def test_other_company_user_changes_blocked(client, manager):
    with pytest.raises(AssertionError) as err:
        await utils.patch_json(client, f"/api/_users/{USERS[0]['_id']}", {"products": []})
    assert "401" in str(err)

    with pytest.raises(AssertionError) as err:
        await utils.delete_json(client, f"/api/_users/{USERS[0]['_id']}", {})
    assert "401" in str(err)

    with pytest.raises(AssertionError) as err:
        await utils.patch_json(client, f"/api/_users/{USERS[1]['_id']}", {"company": COMPANIES[0]["_id"]})
    assert "401" in str(err)


async def test_public_user_can_edit_his_dashboard(app, client, public_user):
    async with app.test_request_context("/") as request:
        request.session["user"] = str(PUBLIC_USER_ID)
        await utils.patch_json(client, f"/api/_users/{PUBLIC_USER_ID}", {"dashboards": []})
