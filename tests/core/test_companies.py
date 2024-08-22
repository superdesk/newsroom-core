from quart import json, url_for
from bson import ObjectId
from newsroom.companies import CompanyServiceAsync as CompanyService, CompanyResource
from newsroom.tests.users import test_login_succeeds_for_admin
from newsroom.tests.fixtures import COMPANY_1_ID

from newsroom.user_roles import UserRole
from newsroom.users.service import UsersService
from tests.utils import logout


async def test_delete_company_deletes_company_and_users(client):
    await test_login_succeeds_for_admin(client)
    # Register a new company
    response = await client.post(
        "/companies/new",
        json={
            "phone": "2132132134",
            "sd_subscriber_id": "12345",
            "name": "Press 2 Co.",
            "is_enabled": True,
            "contact_name": "Tom",
        },
    )

    assert response.status_code == 201
    company: CompanyResource = await CompanyService().find_one(name="Press 2 Co.")

    # Register a user for the company
    response = await client.post(
        "/users/new",
        form={
            "email": "newuser@abc.org",
            "first_name": "John",
            "last_name": "Doe",
            "password": "abc",
            "phone": "1234567",
            "company": company.id,
            "user_type": "public",
        },
    )
    assert response.status_code == 201

    response = await client.delete("/companies/{}".format(company.id))
    assert response.status_code == 200

    user = await UsersService().find_one(email="newuser@abc.org")
    company = await CompanyService().find_by_id(company.id)

    assert user is None
    assert company is None


async def test_company_name_is_unique(client):
    await test_login_succeeds_for_admin(client)
    # Register a new company
    response = await client.post(
        "/companies/new",
        json={
            "phone": "2132132134",
            "sd_subscriber_id": "12345",
            "name": "Press 2 Co.",
            "is_enabled": True,
            "contact_name": "Tom",
        },
    )

    assert response.status_code == 201
    company_id = json.loads(await response.get_data()).get("_id")
    assert company_id

    duplicate_response = await client.post("/companies/new", json={"name": "PRESS 2 Co."})

    assert duplicate_response.status_code == 400
    assert json.loads(await duplicate_response.get_data()).get("name") == "Value must be unique"


async def test_get_company_users(client):
    await test_login_succeeds_for_admin(client)
    resp = await client.post(
        "companies/new",
        json={"name": "Test"},
    )
    company_id = json.loads(await resp.get_data()).get("_id")
    assert company_id
    resp = await client.post(
        "users/new",
        form={
            "company": company_id,
            "first_name": "foo",
            "last_name": "bar",
            "phone": "123456789",
            "email": "foo2@bar.com",
            "user_type": "public",
        },
    )
    assert resp.status_code == 201, (await resp.get_data()).decode("utf-8")
    resp = await client.get("/companies/%s/users" % company_id)
    assert resp.status_code == 200, (await resp.get_data()).decode("utf-8")
    users = json.loads(await resp.get_data())
    assert 1 == len(users)
    assert "foo" == users[0].get("first_name"), users[0].keys()


async def test_save_company_permissions(client, app):
    await logout(client)
    sports_id = ObjectId()
    app.data.insert(
        "products",
        [
            {
                "_id": ObjectId(),
                "name": "Sport",
                "description": "sport product",
                "companies": [COMPANY_1_ID],
                "is_enabled": True,
                "product_type": "wire",
            },
            {
                "_id": sports_id,
                "name": "News",
                "description": "news product",
                "is_enabled": True,
                "product_type": "wire",
                "product_type": "wire",
            },
        ],
    )

    await test_login_succeeds_for_admin(client)
    await client.post(
        f"companies/{COMPANY_1_ID}",
        json={
            "archive_access": True,
            "sections": {"wire": True},
            "products": [{"_id": sports_id, "section": "wire"}],
        },
    )

    updated = app.data.find_one("companies", req=None, _id=COMPANY_1_ID)
    assert updated["sections"]["wire"]
    assert not updated["sections"].get("agenda")
    assert updated["archive_access"]
    assert updated["products"] == [{"section": "wire", "seats": 0, "_id": sports_id}]

    # available by default
    resp = await client.get(url_for("agenda.index"))
    assert resp.status_code == 200

    # set company with wire only
    user = app.data.find_one("users", req=None, first_name="admin")
    assert user
    app.data.update("users", user["_id"], {"company": COMPANY_1_ID, "user_type": UserRole.PUBLIC.value}, user)

    # refresh session with new type
    await logout(client)
    await test_login_succeeds_for_admin(client)

    # test section protection
    resp = await client.get(url_for("agenda.index"))
    assert resp.status_code == 403


async def test_company_ip_whitelist_validation(client):
    new_company = {"name": "Test", "allowed_ip_list": ["wrong"]}
    await test_login_succeeds_for_admin(client)
    resp = await client.post("companies/new", json=new_company)
    assert resp.status_code == 400


async def test_company_auth_domains(client):
    new_company = {"name": "Test", "auth_domains": ["example.com"]}
    resp = await client.post("companies/new", json=new_company)
    assert resp.status_code == 201

    new_company = {"name": "Test 2", "auth_domains": ["example.com"]}
    resp = await client.post("companies/new", json=new_company)
    assert resp.status_code == 400
    assert (await resp.get_json()).get("auth_domains") == "Value must be unique"
