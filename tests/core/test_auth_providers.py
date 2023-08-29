from pytest import fixture
from datetime import datetime, timezone
from unittest import mock

from bson import ObjectId
from flask import url_for

from superdesk import get_resource_service
from newsroom.types import AuthProviderType
from newsroom.tests import markers


companies = {
    "empty_auth": ObjectId(),
    "password_auth": ObjectId(),
    "google_auth": ObjectId(),
    "saml_auth": ObjectId(),
}


@fixture(autouse=True)
def init(app):
    app.config["AUTH_PROVIDERS"].extend(
        [
            {"_id": "gip", "name": "Google", "auth_type": AuthProviderType.GOOGLE_OAUTH.value},
            {"_id": "saml", "name": "Azure", "auth_type": AuthProviderType.SAML.value},
        ]
    )
    app.data.insert(
        "companies",
        [
            {
                "_id": companies["empty_auth"],
                "name": "Empty auth provider",
                "is_enabled": True,
            },
            {
                "_id": companies["password_auth"],
                "name": "Password based auth",
                "is_enabled": True,
                "auth_provider": "newshub",
            },
            {
                "_id": companies["google_auth"],
                "name": "Google based auth",
                "is_enabled": True,
                "auth_provider": "gip",
            },
            {
                "_id": companies["saml_auth"],
                "name": "SAML based auth",
                "is_enabled": True,
                "auth_provider": "saml",
                "auth_domain": "samplecomp",
            },
        ],
    )


def test_password_auth_denies_other_auth_types(app, client):
    users_service = get_resource_service("users")
    user_id = ObjectId()
    app.data.insert(
        "users",
        [
            {
                "_id": user_id,
                "first_name": "John",
                "last_name": "Doe",
                "email": "test@sourcefabric.org",
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "user_type": "administrator",
                "is_validated": True,
                "is_approved": True,
                "is_enabled": True,
                "_created": datetime(2016, 4, 26, 13, 0, 33, tzinfo=timezone.utc),
            }
        ],
    )

    def login_user():
        return client.post(
            url_for("auth.login"),
            data={"email": "test@sourcefabric.org", "password": "admin"},
            follow_redirects=True,
        )

    def test_login_passes():
        login_user()
        with client.session_transaction() as session:
            assert session.get("user") == str(user_id)

        client.get(url_for("auth.logout"), follow_redirects=True)
        with client.session_transaction() as session:
            assert session.get("user") is None

    # Test logging in with administrator with no company
    test_login_passes()

    # Test logging in with public user and company with no ``auth_provider`` assigned
    users_service.patch(id=user_id, updates={"company": companies["empty_auth"], "user_type": "public"})
    test_login_passes()

    # Test logging in with public user and company with ``auth_provider`` set to a password based one
    users_service.patch(id=user_id, updates={"company": companies["password_auth"]})
    test_login_passes()

    # Test logging in fails with public user and company with ``auth_provider`` set to use OAuth
    users_service.patch(id=user_id, updates={"company": companies["google_auth"]})
    response = login_user()
    assert "Invalid login type" in response.get_data(as_text=True)

    # Test logging in fails with public user and company with ``auth_provider`` set to use SAML
    users_service.patch(id=user_id, updates={"company": companies["saml_auth"]})
    response = login_user()
    assert "Invalid login type" in response.get_data(as_text=True)

    # Test logging in with password, as administrator and company with ``auth_provider`` set to SAML
    # This is used as a fallback option so admins can always login
    users_service.patch(id=user_id, updates={"company": companies["saml_auth"], "user_type": "administrator"})
    test_login_passes()


class MockSAMLAuth:
    def process_response(self):
        pass

    def get_errors(self):
        return []

    def get_nameid(self):
        return "foo@samplecomp"

    def get_session_index(self):
        return "abcd123"

    def get_attributes(self):
        return {
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname": ["Foo"],
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname": ["Bar"],
        }


def mock_saml_client(req):
    return MockSAMLAuth()


@markers.enable_saml
@mock.patch("newsroom.auth.saml.init_saml_auth", mock_saml_client)
def test_saml_auth_denies_other_auth_types(app, client):
    app.config["SAML_CLIENTS"] = ["samplecomp"]
    users_service = get_resource_service("users")
    companies_service = get_resource_service("companies")

    def login_user():
        resp = client.get("/login/samplecomp", follow_redirects=True)
        assert 200 == resp.status_code
        return client.get("/login/saml?acs=1", follow_redirects=True)

    # Test logging in fails with ``auth_provider`` not defined
    companies_service.patch(companies["saml_auth"], updates={"auth_provider": None})
    response = login_user()
    assert "Invalid login type" in response.get_data(as_text=True)

    # Test logging in fails with ``auth_provider`` set to a password based one
    companies_service.patch(companies["saml_auth"], updates={"auth_provider": "newshub"})
    response = login_user()
    assert "Invalid login type" in response.get_data(as_text=True)

    # Test logging in fails with ``auth_provider`` set to use OAuth
    companies_service.patch(companies["saml_auth"], updates={"auth_provider": "gip"})
    response = login_user()
    assert "Invalid login type" in response.get_data(as_text=True)

    # Test logging in with ``auth_provider`` set to use SAML
    companies_service.patch(companies["saml_auth"], updates={"auth_provider": "saml"})
    login_user()
    user = users_service.find_one(req=None, email="foo@samplecomp")
    assert user is not None
    with client.session_transaction() as session:
        assert session.get("user") == str(user["_id"])


class MockGoogleOAuth:
    def authorize_access_token(self):
        return "token123"

    def parse_id_token(self, token):
        return {"email": "google_test@sourcefabric.org"}


class MockOAuth:
    google = MockGoogleOAuth()

    def register(self):
        pass


@markers.enable_google_login
def test_google_oauth_denies_other_auth_types(app, client):
    companies_service = get_resource_service("companies")
    user_id = ObjectId()
    app.data.insert(
        "users",
        [
            {
                "_id": user_id,
                "first_name": "John",
                "last_name": "Doe",
                "email": "google_test@sourcefabric.org",
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "user_type": "administrator",
                "is_validated": True,
                "is_approved": True,
                "is_enabled": True,
                "_created": datetime(2016, 4, 26, 13, 0, 33, tzinfo=timezone.utc),
            }
        ],
    )

    with mock.patch("newsroom.auth.oauth.oauth", MockOAuth()):
        # Test logging in fails with no company assigned
        response = client.get("/login/google_authorized", follow_redirects=True)
        assert "Invalid login type" in response.get_data(as_text=True)

        # Test logging in fails with ``auth_provider`` not defined
        get_resource_service("users").patch(
            user_id, updates={"company": companies["google_auth"], "user_type": "public"}
        )
        companies_service.patch(companies["google_auth"], updates={"auth_provider": None})
        response = client.get("/login/google_authorized", follow_redirects=True)
        assert "Invalid login type" in response.get_data(as_text=True)

        # Test logging in fails with ``auth_provider`` set to a password based one
        companies_service.patch(companies["google_auth"], updates={"auth_provider": "newshub"})
        response = client.get("/login/google_authorized", follow_redirects=True)
        assert "Invalid login type" in response.get_data(as_text=True)

        # Test logging in fails with ``auth_provider`` set to use SAML
        companies_service.patch(companies["google_auth"], updates={"auth_provider": "saml"})
        response = client.get("/login/google_authorized", follow_redirects=True)
        assert "Invalid login type" in response.get_data(as_text=True)

        # Test logging in with ``auth_provider`` set to use Google OAuth
        companies_service.patch(companies["google_auth"], updates={"auth_provider": "gip"})
        client.get("/login/google_authorized", follow_redirects=True)
        with client.session_transaction() as session:
            assert session.get("user") == str(user_id)
