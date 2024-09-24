import pytest

from pydantic import ValidationError
from bson import ObjectId

from newsroom.auth.saml import get_userdata
from newsroom.companies import CompanyServiceAsync, CompanyResource


async def test_user_data_with_matching_company(app):
    company = {
        "name": "test",
        "auth_domains": ["example.com"],
    }
    app.data.insert("companies", [company])

    saml_data = {
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname": ["Foo"],
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname": ["Bar"],
    }

    async with app.test_request_context("/login/saml"):
        user_data = get_userdata("foo@example.com", saml_data)
        assert user_data.get("company") == company["_id"]
        assert user_data.get("user_type") == "public"

        user_data = get_userdata("foo@newcomp.com", saml_data)
        assert user_data.get("company") is None
        assert user_data.get("user_type") == "internal"


async def test_user_data_with_matching_preconfigured_client(app, client):
    company = {
        "name": "test",
        "auth_domains": ["samplecomp"],
    }

    app.data.insert("companies", [company])

    saml_data = {
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname": ["Foo"],
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname": ["Bar"],
    }

    resp = await client.get("/login/samplecomp")
    assert 404 == resp.status_code

    async with app.test_request_context("/login/saml"):
        user_data = get_userdata("foo@example.com", saml_data)
        assert "company" not in user_data

    app.config["SAML_CLIENTS"] = ["samplecomp"]

    async with app.test_client() as c:
        resp = await c.get("/login/samplecomp")
        assert 200 == resp.status_code

        user_data = get_userdata("foo@example.com", saml_data)
        assert user_data.get("company") == company["_id"]
        assert user_data.get("user_type") == "public"

    app.data.update("companies", company["_id"], {"internal": True}, company)

    with app.test_client() as c:
        resp = c.get("/login/samplecomp")
        assert 200 == resp.status_code

        user_data = get_userdata("foo@example.com", saml_data)
        assert user_data.get("company") == company["_id"]
        assert user_data.get("user_type") == "internal"


def test_get_userdata_without_first_last_name(app):
    saml_data = {
        "http://schemas.microsoft.com/identity/claims/displayname": ["Foo Bar"],
    }

    with app.test_request_context():
        user_data = get_userdata("foo@example.com", saml_data)
        assert "Foo" == user_data["first_name"]
        assert "Bar" == user_data["last_name"]


async def test_company_auth_domains(app, client):
    service = CompanyServiceAsync()

    await service.create([CompanyResource(id=ObjectId(), name="test", auth_domains=["example.com"])])

    def assert_unique_domain_error(validation_error):
        errors = validation_error.value.errors()
        assert errors[0]["type"] == "unique"
        assert errors[0]["loc"] == ("auth_domains",)

    with pytest.raises(ValidationError) as error:
        await service.create([CompanyResource(id=ObjectId(), name="test2", auth_domains=["example.com"])])
    assert_unique_domain_error(error)

    with pytest.raises(ValidationError) as error:
        await service.create([CompanyResource(id=ObjectId(), name="TEST2", auth_domains=["EXAMPLE.COM"])])
    assert_unique_domain_error(error)

    ids = await service.create(
        [
            CompanyResource(id=ObjectId(), name="test3", auth_domains=[]),
            CompanyResource(id=ObjectId(), name="test4", auth_domains=["foo.com", "bar.com"]),
        ]
    )

    with pytest.raises(ValidationError) as error:
        await service.create([CompanyResource(id=ObjectId(), name="test6", auth_domains=["unique.com", "example.com"])])
    assert_unique_domain_error(error)

    with pytest.raises(ValidationError) as error:
        await service.update(ids[0], dict(auth_domains=["unique.com", "example.com"]))
    assert_unique_domain_error(error)
