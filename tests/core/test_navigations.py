from bson import ObjectId
from quart import json
from pytest import fixture
from newsroom.navigations.views import add_remove_products_for_navigation
from newsroom.products.products import get_products_by_navigation

from newsroom.products.views import get_product_ref
from newsroom.tests.users import test_login_succeeds_for_admin  # noqa
from newsroom.tests.fixtures import COMPANY_1_ID
from newsroom.navigations import get_navigations
from newsroom.types import Product
from tests.core.utils import add_company_products, create_entries_for


NAV_ID = ObjectId("59b4c5c61d41c8d736852fbf")
AGENDA_NAV_ID = ObjectId()


@fixture(autouse=True)
async def navigations():
    await create_entries_for(
        "navigations",
        [
            {
                "_id": NAV_ID,
                "name": "Sport",
                "product_type": "wire",
                "description": "Top level sport navigation",
                "is_enabled": True,
            },
            {
                "_id": AGENDA_NAV_ID,
                "name": "Calendar",
                "product_type": "agenda",
                "is_enabled": True,
            },
        ],
    )


async def test_navigation_list_succeeds_for_anonymous_user(client):
    response = await client.get("/navigations")
    assert response.status_code == 200
    assert b"Sport" in await response.get_data()


async def test_save_and_return_navigations(client):
    await test_login_succeeds_for_admin(client)
    # Save a new navigation
    await client.post(
        "/navigations/new",
        form={
            "navigation": json.dumps(
                {
                    "name": "Breaking",
                    "description": "Breaking news",
                    "product_type": "wire",
                    "is_enabled": True,
                }
            )
        },
    )

    response = await client.get("/navigations")
    assert "Breaking" in await response.get_data(as_text=True)


async def test_update_navigation(client):
    await test_login_succeeds_for_admin(client)

    await client.post(
        "/navigations/59b4c5c61d41c8d736852fbf/",
        form={
            "navigation": json.dumps(
                {
                    "name": "Sport",
                    "description": "foo",
                    "product_type": "wire",
                    "is_enabled": True,
                }
            )
        },
    )

    response = await client.get("/navigations")
    assert "foo" in await response.get_data(as_text=True)


async def test_delete_navigation_removes_references(client):
    await test_login_succeeds_for_admin(client)

    await client.post(
        "/products/new",
        json={
            "name": "Breaking",
            "description": "Breaking news",
            "navigations": ["59b4c5c61d41c8d736852fbf"],
            "is_enabled": True,
            "product_type": "wire",
            "query": "foo",
        },
    )

    await client.delete("/navigations/59b4c5c61d41c8d736852fbf")

    response = await client.get("/products")
    data = json.loads(await response.get_data())
    assert 1 == len(data)
    assert data[0]["name"] == "Breaking"
    assert data[0]["navigations"] == []


async def test_create_navigation_with_products(client, app):
    app.data.insert(
        "products",
        [
            {
                "_id": "p-1",
                "name": "Sport",
                "description": "sport product",
                "navigations": [],
                "is_enabled": True,
                "product_type": "wire",
            },
            {
                "_id": "p-2",
                "name": "News",
                "description": "news product",
                "navigations": [],
                "is_enabled": True,
                "product_type": "wire",
            },
        ],
    )

    await test_login_succeeds_for_admin(client)
    response = await client.post(
        "/navigations/new",
        form={
            "navigation": json.dumps(
                {
                    "name": "Breaking",
                    "description": "Breaking news",
                    "product_type": "wire",
                    "is_enabled": True,
                    "products": ["p-2"],
                }
            )
        },
    )
    assert response.status_code == 201
    nav_id = json.loads(await response.get_data()).get("_id")
    assert nav_id

    response = await client.get("/navigations")
    assert "Breaking news" in await response.get_data(as_text=True)

    response = await client.get("/products")
    data = json.loads(await response.get_data())
    assert [p for p in data if p["_id"] == "p-1"][0]["navigations"] == []
    assert [p for p in data if p["_id"] == "p-2"][0]["navigations"] == [nav_id]


async def test_update_navigation_with_products(client, app):
    app.data.insert(
        "products",
        [
            {
                "_id": "p-1",
                "name": "Sport",
                "description": "sport product",
                "navigations": [],
                "is_enabled": True,
                "product_type": "wire",
            },
            {
                "_id": "p-2",
                "name": "News",
                "description": "news product",
                "navigations": [NAV_ID],
                "is_enabled": True,
                "product_type": "wire",
            },
        ],
    )

    await test_login_succeeds_for_admin(client)
    await client.post(
        f"navigations/{NAV_ID}",
        form={"navigation": json.dumps({"name": "Sports 2", "is_enabled": True, "products": ["p-1"]})},
    )

    response = await client.get("/products")
    data = json.loads(await response.get_data())
    assert [p for p in data if p["_id"] == "p-1"][0]["navigations"] == [str(NAV_ID)]
    assert [p for p in data if p["_id"] == "p-2"][0]["navigations"] == []


async def test_get_agenda_navigations_by_company_returns_ordered(client, app):
    await create_entries_for(
        "navigations",
        [
            {
                "_id": "66e7f7806fe6d08ae60a15b9",
                "name": "Uber",
                "is_enabled": True,
                "product_type": "agenda",
            }
        ],
    )

    add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "name": "Top Things",
                "navigations": [ObjectId("66e7f7806fe6d08ae60a15b9")],
                "is_enabled": True,
                "query": "_featured",
                "product_type": "agenda",
            },
            {
                "name": "A News",
                "navigations": [ObjectId("59b4c5c61d41c8d736852fbf")],
                "description": "news product",
                "is_enabled": True,
                "product_type": "wire",
                "query": "latest",
            },
        ],
    )

    await test_login_succeeds_for_admin(client)
    company = app.data.find_one("companies", req=None, _id=COMPANY_1_ID)
    navigations = await get_navigations(None, company, "agenda")
    assert navigations[0].get("name") == "Uber"
    navigations = await get_navigations(None, company, "wire")
    assert navigations[0].get("name") == "Sport"


async def test_get_products_by_navigation_caching(app):
    nav_id = ObjectId()
    await create_entries_for(
        "navigations",
        [
            {
                "_id": nav_id,
                "name": "Uber",
                "is_enabled": True,
                "product_type": "agenda",
            }
        ],
    )

    app.data.insert(
        "products",
        [
            {
                "_id": "p-2",
                "name": "A News",
                "navigations": [nav_id],
                "description": "news product",
                "is_enabled": True,
                "product_type": "wire",
                "query": "latest",
            },
        ],
    )

    # using new context to avoid caching via flask.g
    async with app.app_context():
        assert 1 == len(get_products_by_navigation([nav_id], "wire"))

    await add_remove_products_for_navigation(nav_id, [])

    async with app.app_context():
        assert 0 == len(get_products_by_navigation([nav_id], "wire"))


async def test_get_navigations_for_admin(admin):
    navigations = await get_navigations(admin, None, "wire")
    assert 1 == len(navigations)
    assert "Sport" == navigations[0]["name"]

    navigations = await get_navigations(admin, None, "agenda")
    assert 1 == len(navigations)
    assert "Calendar" == navigations[0]["name"]


async def test_get_navigations_for_user(public_user, public_company, app):
    navigations = await get_navigations(public_user, public_company, "wire")
    assert 0 == len(navigations)

    navigations = await get_navigations(public_user, public_company, "agenda")
    assert 0 == len(navigations)

    products = [
        Product(
            _id=ObjectId(),
            name="Wire",
            navigations=[NAV_ID],
            is_enabled=True,
            product_type="wire",
        ),
        Product(
            _id=ObjectId(),
            name="Agenda",
            navigations=[AGENDA_NAV_ID],
            is_enabled=True,
            product_type="agenda",
        ),
    ]

    app.data.insert("products", products)
    public_user["products"] = [get_product_ref(products[0]), get_product_ref(products[1])]

    navigations = await get_navigations(public_user, public_company, "wire")
    assert 1 == len(navigations)
    assert "Sport" == navigations[0]["name"]

    navigations = await get_navigations(public_user, public_company, "agenda")
    assert 1 == len(navigations)
    assert "Calendar" == navigations[0]["name"]
