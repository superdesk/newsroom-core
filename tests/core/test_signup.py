from unittest import mock

from quart import url_for

from newsroom.types import CompanyType, Country
from newsroom.auth import get_auth_user_by_email
from newsroom.companies.companies_async import CompanyService, CompanyProduct
from newsroom.products.types import ProductType

from tests.utils import get_user_by_email, mock_send_email


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_new_user_signup_sends_email(app, client):
    company_service = CompanyService()
    app.countries = [Country(value="AUS", text="Australia")]
    app.config["SIGNUP_EMAIL_RECIPIENTS"] = "admin@bar.com"
    app.config["COMPANY_TYPES"] = [CompanyType(id="news_media", name="News Media")]
    product_ids = app.data.insert(
        "products", [{"name": "test", "query": "foo", "is_enabled": True, "product_type": "wire"}]
    )
    with app.mail.record_messages() as outbox:
        # Sign up
        response = await client.post(
            url_for("auth.signup"),
            form={
                "email": "newuser@abc.org",
                "first_name": "John",
                "last_name": "Doe",
                "country": "AUS",
                "phone": "1234567",
                "company": "News Press Co.",
                "company_size": "0-10",
                "occupation": "Other",
                "company_type": "news_media",
            },
        )
        assert response.status_code == 200

        assert len(outbox) == 1
        assert outbox[0].recipients == ["admin@bar.com"]
        assert outbox[0].subject == "A new Newshub signup request"
        assert "newuser@abc.org" in outbox[0].body
        assert "John" in outbox[0].body
        assert "Doe" in outbox[0].body
        assert "1234567" in outbox[0].body
        assert "News Press Co." in outbox[0].body
        assert "Australia" in outbox[0].body
        assert "News Media" in outbox[0].body

    # Test that the new Company has been created
    new_company = await company_service.find_one(name="News Press Co.")
    assert new_company is not None
    assert new_company.contact_name == "John Doe"
    assert new_company.contact_email == "newuser@abc.org"
    assert new_company.phone == "1234567"
    assert new_company.country == "AUS"
    assert new_company.company_type == "news_media"
    assert new_company.is_enabled is False
    assert new_company.is_approved is False
    assert new_company.sections == {
        "wire": True,
        "agenda": True,
        "news_api": True,
        "monitoring": True,
    }
    assert new_company.products == [
        CompanyProduct(
            _id=product_ids[0],
            section=ProductType.WIRE,
            seats=0,
        )
    ]

    # Test that the new User has been created
    new_user = app.data.find_one("users", req=None, email="newuser@abc.org")
    assert new_user is not None
    assert new_user["first_name"] == "John"
    assert new_user["last_name"] == "Doe"
    assert new_user["email"] == "newuser@abc.org"
    assert new_user["phone"] == "1234567"
    assert new_user["role"] == "Other"
    assert new_user["country"] == "AUS"
    assert new_user["company"] == new_company.id
    assert new_user["is_enabled"] is False
    assert new_user["is_approved"] is False
    assert new_user["is_validated"] is False
    assert new_user["sections"] == {
        "wire": True,
        "agenda": True,
        "news_api": True,
        "monitoring": True,
    }


async def test_new_user_signup_fails_if_fields_not_provided(client, app):
    app.config["SIGNUP_EMAIL_RECIPIENTS"] = "admin@bar.com"
    # Register a new account
    response = await client.post(
        url_for("auth.signup"),
        form={
            "email": "newuser@abc.org",
            "email2": "newuser@abc.org",
            "phone": "1234567",
            "password": "abc",
            "password2": "abc",
        },
    )
    txt = await response.get_data(as_text=True)
    assert "company: This field is required" in txt
    assert "company_size: This field is required" in txt
    assert "name: This field is required" in txt
    assert "country: This field is required" in txt
    assert "occupation: This field is required" in txt


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_approve_company_and_users(app, client):
    app.countries = [Country(value="AUS", text="Australia")]
    app.config["SIGNUP_EMAIL_RECIPIENTS"] = "admin@bar.com"
    app.config["COMPANY_TYPES"] = [CompanyType(id="news_media", name="News Media")]

    # Sign up a new Company & User
    with app.mail.record_messages():
        response = await client.post(
            url_for("auth.signup"),
            form={
                "email": "john@doe.org",
                "first_name": "John",
                "last_name": "Doe",
                "country": "AUS",
                "phone": "1234567",
                "company": "Doe Press Co.",
                "company_size": "0-10",
                "occupation": "Other",
                "company_type": "news_media",
            },
        )
        assert response.status_code == 200

    # Test the Company & User are not enabled nor approved
    new_company = app.data.find_one("companies", req=None, name="Doe Press Co.")
    assert new_company["is_enabled"] is False
    assert new_company["is_approved"] is False

    new_user = await get_user_by_email("john@doe.org")
    assert new_user["is_enabled"] is False
    assert new_user["is_approved"] is False
    assert new_user["is_validated"] is False

    # Approve the new Company and it's associated User
    with app.mail.record_messages() as outbox:
        response = await client.post(url_for("companies.approve_company", company_id=str(new_company["_id"])))
        assert response.status_code == 200

        # Test the Company & User are now enabled and approved, but not yet validated
        new_company = app.data.find_one("companies", req=None, name="Doe Press Co.")
        assert new_company["is_enabled"] is True
        assert new_company["is_approved"] is True

        new_user = await get_user_by_email("john@doe.org")
        assert new_user["is_enabled"] is True
        assert new_user["is_approved"] is True
        assert new_user["is_validated"] is False

        # Test that the account activation email was sent
        auth_user = get_auth_user_by_email("john@doe.org")
        assert len(outbox) == 1
        assert outbox[0].recipients == ["john@doe.org"]
        assert outbox[0].subject == "Newshub account created"
        assert auth_user["token"] in outbox[0].body

    # Sign up another user for the same company
    response = await client.post(
        url_for("auth.signup"),
        form={
            "email": "jane@doe.org",
            "first_name": "Jane",
            "last_name": "Doe",
            "country": "AUS",
            "phone": "1234567",
            "company": "Doe Press Co.",
            "company_size": "0-10",
            "occupation": "Other",
            "company_type": "news_media",
        },
    )
    assert response.status_code == 200

    # Test the Company is enabled and approved, but new User is not
    new_company = app.data.find_one("companies", req=None, name="Doe Press Co.")
    assert new_company["is_enabled"] is True
    assert new_company["is_approved"] is True
    new_user = app.data.find_one("users", req=None, email="jane@doe.org")
    assert new_user["is_enabled"] is False
    assert new_user["is_approved"] is False
    assert new_user["is_validated"] is False

    # Approve the new User
    with app.mail.record_messages() as outbox:
        response = await client.post(url_for("users_views.approve_user", user_id=str(new_user["_id"])))
        assert response.status_code == 200

        # Test the new User is now enabled and approved, but not yet validated
        new_user = await get_user_by_email("jane@doe.org")
        assert new_user["is_enabled"] is True
        assert new_user["is_approved"] is True
        assert new_user["is_validated"] is False

        # Test that the account activation email was sent
        auth_user = get_auth_user_by_email("jane@doe.org")
        assert len(outbox) == 1
        assert outbox[0].recipients == ["jane@doe.org"]
        assert outbox[0].subject == "Newshub account created"
        assert auth_user["token"] in outbox[0].body


async def test_signup_not_enabled_without_config(client, app):
    app.config["SIGNUP_EMAIL_RECIPIENTS"] = ""

    response = await client.get(url_for("auth.signup"))
    assert response.status_code == 404

    app.config["SIGNUP_EMAIL_RECIPIENTS"] = "foo"

    response = await client.get(url_for("auth.signup"))
    assert response.status_code == 200
