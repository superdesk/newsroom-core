import pytest
import werkzeug.exceptions

from newsroom.auth.saml import get_userdata


def test_user_data_with_matching_company(app):
    company = {
        "name": "test",
        "auth_domains": ["example.com"],
    }
    app.data.insert("companies", [company])

    saml_data = {
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname": ["Foo"],
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname": ["Bar"],
    }

    with app.test_request_context():
        user_data = get_userdata("foo@example.com", saml_data)
        assert user_data.get("company") == company["_id"]
        assert user_data.get("user_type") == "public"

        user_data = get_userdata("foo@newcomp.com", saml_data)
        assert user_data.get("company") is None
        assert user_data.get("user_type") == "internal"


def test_user_data_with_matching_preconfigured_client(app, client):
    company = {
        "name": "test",
        "auth_domains": ["samplecomp"],
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
        assert user_data.get("user_type") == "public"

    app.data.update("companies", company["_id"], {"internal": True}, company)

    with app.test_client() as c:
        resp = c.get("/login/samplecomp")
        assert 200 == resp.status_code

        user_data = get_userdata("foo@example.com", saml_data)
        assert user_data.get("company") == company["_id"]
        assert user_data.get("user_type") == "internal"


def test_company_auth_domains(app):
    app.data.insert("companies", [{"name": "test", "auth_domains": ["example.com"]}])
    assert app.data.find_one("companies", req=None, auth_domains="example.com") is not None
    with pytest.raises(werkzeug.exceptions.Conflict):
        app.data.insert("companies", [{"name": "test2", "auth_domains": ["example.com"]}])
    with pytest.raises(werkzeug.exceptions.Conflict):
        app.data.insert("companies", [{"name": "TEST2", "auth_domains": ["EXAMPLE.COM"]}])
    app.data.insert("companies", [{"name": "test3", "auth_domains": []}])
    app.data.insert("companies", [{"name": "test4", "auth_domains": ["foo.com", "bar.com"]}])
    assert app.data.find_one("companies", req=None, auth_domains="bar.com") is not None
    with pytest.raises(werkzeug.exceptions.Conflict):
        app.data.insert("companies", [{"name": "test6", "auth_domains": ["unique.com", "example.com"]}])
