from pytest import fixture
from datetime import datetime, timezone
from unittest import mock

from bson import ObjectId
from quart import url_for

from newsroom.users.service import UsersService
from superdesk import get_resource_service
from newsroom.types import AuthProviderType
from newsroom.tests import markers
from tests.utils import get_user_by_email, logout


companies = {
    "empty_auth": ObjectId(),
    "password_auth": ObjectId(),
    "google_auth": ObjectId(),
    "saml_auth": ObjectId(),
}


@fixture(autouse=True)
async def init(app):
    app.config["AUTH_PROVIDERS"].extend(
        [
            {"_id": "gip", "name": "Google", "auth_type": AuthProviderType.GOOGLE_OAUTH},
            {"_id": "saml", "name": "Azure", "auth_type": AuthProviderType.SAML},
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
                "auth_domains": ["samplecomp"],
            },
        ],
    )


async def test_password_auth_denies_other_auth_types(app, client):
    from newsroom.users.service import UsersService

    await logout(client)
    users_service = UsersService()

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

    async def login_user():
        # return await login(client, {"email": "test@sourcefabric.org", "password": "admin"})
        return await client.post(
            url_for("auth.login"),
            form={"email": "test@sourcefabric.org", "password": "admin"},
            follow_redirects=True,
        )

    async def test_login_passes():
        await login_user()
        async with client.session_transaction() as session:
            assert session.get("user") == str(user_id)

        await client.get(url_for("auth.logout"), follow_redirects=True)
        async with client.session_transaction() as session:
            assert session.get("user") is None

    # Test logging in with administrator with no company
    await test_login_passes()

    # Test logging in with public user and company with no ``auth_provider`` assigned
    await users_service.update(user_id, updates={"company": companies["empty_auth"], "user_type": "public"})
    await test_login_passes()

    # Test logging in with public user and company with ``auth_provider`` set to a password based one
    await users_service.update(user_id, updates={"company": companies["password_auth"]})
    await test_login_passes()

    # Test logging in fails with public user and company with ``auth_provider`` set to use OAuth
    await users_service.update(user_id, updates={"company": companies["google_auth"]})
    response = await login_user()
    assert "Invalid login type" in await response.get_data(as_text=True)

    # Test logging in fails with public user and company with ``auth_provider`` set to use SAML
    await users_service.update(user_id, updates={"company": companies["saml_auth"]})
    response = await login_user()
    assert "Invalid login type" in await response.get_data(as_text=True)

    # Test logging in with password, as administrator and company with ``auth_provider`` set to SAML
    # This is used as a fallback option so admins can always login
    await users_service.update(user_id, updates={"company": companies["saml_auth"], "user_type": "administrator"})
    await test_login_passes()


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
async def test_saml_auth_denies_other_auth_types(app, client):
    await logout(client)
    app.config["SAML_CLIENTS"] = ["samplecomp"]
    companies_service = get_resource_service("companies")

    async def login_user():
        resp = await client.get("/login/samplecomp", follow_redirects=True)
        assert 200 == resp.status_code
        return await client.get("/login/saml?acs=1", follow_redirects=True)

    # Test logging in fails with ``auth_provider`` not defined
    companies_service.patch(companies["saml_auth"], updates={"auth_provider": None})
    response = await login_user()
    assert "Invalid login type" in await response.get_data(as_text=True)

    # Test logging in fails with ``auth_provider`` set to a password based one
    companies_service.patch(companies["saml_auth"], updates={"auth_provider": "newshub"})
    response = await login_user()
    assert "Invalid login type" in await response.get_data(as_text=True)

    # Test logging in fails with ``auth_provider`` set to use OAuth
    companies_service.patch(companies["saml_auth"], updates={"auth_provider": "gip"})
    response = await login_user()
    assert "Invalid login type" in await response.get_data(as_text=True)

    # Test logging in with ``auth_provider`` set to use SAML
    companies_service.patch(companies["saml_auth"], updates={"auth_provider": "saml"})
    response = await login_user()
    assert "Invalid login type" not in await response.get_data(as_text=True)

    user = await get_user_by_email("foo@samplecomp")
    assert user is not None
    async with client.session_transaction() as session:
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
async def test_google_oauth_denies_other_auth_types(app, client):
    await logout(client)
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
        response = await client.get("/login/google_authorized", follow_redirects=True)
        assert "Invalid login type" in await response.get_data(as_text=True)

        # Test logging in fails with ``auth_provider`` not defined
        await UsersService().update(user_id, updates={"company": companies["google_auth"], "user_type": "public"})
        companies_service.patch(companies["google_auth"], updates={"auth_provider": None})
        response = await client.get("/login/google_authorized", follow_redirects=True)
        assert "Invalid login type" in await response.get_data(as_text=True)

        # Test logging in fails with ``auth_provider`` set to a password based one
        companies_service.patch(companies["google_auth"], updates={"auth_provider": "newshub"})
        response = await client.get("/login/google_authorized", follow_redirects=True)
        assert "Invalid login type" in await response.get_data(as_text=True)

        # Test logging in fails with ``auth_provider`` set to use SAML
        companies_service.patch(companies["google_auth"], updates={"auth_provider": "saml"})
        response = await client.get("/login/google_authorized", follow_redirects=True)
        assert "Invalid login type" in await response.get_data(as_text=True)

        # Test logging in with ``auth_provider`` set to use Google OAuth
        companies_service.patch(companies["google_auth"], updates={"auth_provider": "gip"})
        await client.get("/login/google_authorized", follow_redirects=True)
        async with client.session_transaction() as session:
            assert session.get("user") == str(user_id)
