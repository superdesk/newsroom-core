import pytest
import werkzeug.exceptions

from newsroom.auth.saml import get_userdata


def test_user_data_with_matching_company(app):
    company = {
        "name": "test",
        "auth_domain": "example.com",
    }
    app.data.insert("companies", [company])

    saml_data = {
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname": ["Foo"],
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname": ["Bar"],
    }

    with app.test_request_context():
        user_data = get_userdata("foo@example.com", saml_data)
        assert user_data.get("company") == company["_id"]

        user_data = get_userdata("foo@newcomp.com", saml_data)
        assert user_data.get("company") is None


def test_user_data_with_matching_preconfigured_client(app, client):
    company = {
        "name": "test",
        "auth_domain": "samplecomp",
    }

    app.data.insert("companies", [company])

    saml_data = {
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname": ["Foo"],
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname": ["Bar"],
    }

    with app.test_client() as c:
        resp = c.get("/login/samplecomp")
        assert 404 == resp.status_code

        user_data = get_userdata("foo@example.com", saml_data)
        assert "company" not in user_data

    app.config["SAML_CLIENTS"] = ["samplecomp"]

    with app.test_client() as c:
        resp = c.get("/login/samplecomp")
        assert 200 == resp.status_code

        user_data = get_userdata("foo@example.com", saml_data)
        assert user_data.get("company") == company["_id"]


def test_auth_domain_unique_for_company(app):
    app.data.insert("companies", [{"name": "test", "auth_domain": "example.com"}])
    with pytest.raises(werkzeug.exceptions.Conflict):
        app.data.insert("companies", [{"name": "test2", "auth_domain": "example.com"}])
    with pytest.raises(werkzeug.exceptions.Conflict):
        app.data.insert("companies", [{"name": "TEST2", "auth_domain": "EXAMPLE.COM"}])
    app.data.insert("companies", [{"name": "test3", "auth_domain": None}])
    app.data.insert("companies", [{"name": "test4", "auth_domain": None}])
    app.data.insert("companies", [{"name": "test5", "auth_domain": ""}])
    app.data.insert("companies", [{"name": "test6", "auth_domain": ""}])
