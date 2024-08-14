from bson import ObjectId
from quart import json
from pytest import fixture

from newsroom.tests.users import test_login_succeeds_for_admin
from tests import utils


@fixture(autouse=True)
async def init(app):
    app.data.insert(
        "section_filters",
        [
            {
                "_id": ObjectId("59b4c5c61d41c8d736852fbf"),
                "name": "Sport",
                "description": "Sports Filter",
                "is_enabled": True,
            }
        ],
    )


async def test_filter_list_fails_for_anonymous_user(app, anonymous_user, public_user):
    async with app.test_client() as client:
        res = await client.get("/section_filters/search", follow_redirects=False)
        assert res.status_code == 302
        assert res.headers.get("location") == "/login"

    async with app.test_client() as client:
        await utils.login(client, public_user)
        response = await client.get("/section_filters/search")
        assert response.status_code == 403
        assert b"Forbidden" in await response.get_data()


async def test_return_search_for_filters(client):
    await test_login_succeeds_for_admin(client)
    await client.post(
        "/section_filters/new",
        json={
            "name": "Breaking",
            "description": "Breaking news",
            "is_enabled": True,
            "sd_product_id": "123",
        }
    )

    response = await client.get("/section_filters/search?q=br")
    assert "Breaking" in await response.get_data(as_text=True)


async def test_create_fails_in_validation(client):
    await test_login_succeeds_for_admin(client)
    response = await client.post(
        "/section_filters/new",
        json={
            "description": "Breaking news",
            "is_enabled": True,
        }
    )

    assert response.status_code == 400
    assert "name" in await response.get_data(as_text=True)


async def test_update_filters(client):
    await test_login_succeeds_for_admin(client)

    resp = await client.post(
        "/section_filters/59b4c5c61d41c8d736852fbf",
        json={
            "name": "Sport",
            "description": "foo",
            "is_enabled": True,
            "sd_product_id": "123",
        }
    )

    assert 200 == resp.status_code

    response = await client.get("/section_filters")
    assert "foo" in await response.get_data(as_text=True)


async def test_delete_product(client):
    await test_login_succeeds_for_admin(client)

    await client.post(
        "/section_filters/new",
        json={
            "name": "Breaking",
            "description": "Breaking news",
            "parents": "59b4c5c61d41c8d736852fbf",
            "is_enabled": True,
            "query": "bar",
        }
    )

    resp = await client.delete("/section_filters/59b4c5c61d41c8d736852fbf")
    assert 200 == resp.status_code

    response = await client.get("/section_filters")
    data = json.loads(await response.get_data())
    assert 1 == len(data)
    assert data[0]["name"] == "Breaking"


async def test_gets_all_products(client, app):
    await test_login_succeeds_for_admin(client)

    for i in range(250):
        app.data.insert(
            "section_filters",
            [
                {
                    "name": "Sport-%s" % i,
                    "description": "Top level sport product",
                    "is_enabled": True,
                }
            ],
        )

    resp = await client.get("/section_filters")
    data = json.loads(await resp.get_data())
    assert 251 == len(data)
