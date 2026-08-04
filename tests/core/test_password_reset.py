from unittest.mock import patch
from datetime import timedelta
from contextlib import contextmanager
from uuid import uuid4

from superdesk import get_resource_service
from superdesk.utc import utcnow

from newsroom.auth.utils import get_token_data, hash_login_token
from newsroom.types import AuthProviderType
from newsroom.tests.fixtures import COMPANY_1_ID
from newsroom.users import UsersAuthService


async def test_password_reset(client, app):
    resp = await client.get("/token/reset_password")
    assert 200 == resp.status_code, await resp.get_data(as_text=True)

    with patch("newsroom.auth.utils.send_reset_password_email") as send_email_mock:
        resp = await client.post("/token/reset_password", form={"email": "foo@bar.com"})
        assert 302 == resp.status_code, await resp.get_data(as_text=True)
        send_email_mock.assert_called_once()
        user, token = send_email_mock.call_args.args

    assert user
    assert token

    users_service = UsersAuthService()
    token_owner = await users_service.get_by_email("foo@bar.com")
    assert token_owner is not None
    assert token_owner.token == hash_login_token(token)

    resp = await client.get(f"/reset_password/{token}")
    assert 200 == resp.status_code, await resp.get_data(as_text=True)

    resp = await client.post(
        f"/reset_password/{token}", form={"new_password": "newpassword", "new_password2": "newpassword"}
    )
    assert 302 == resp.status_code, await resp.get_data(as_text=True)


async def test_password_reset_uses_firebase_admin_for_firebase_auth(client, app):
    app.config["AUTH_PROVIDERS"].append({"_id": "firebase", "name": "Firebase", "auth_type": AuthProviderType.FIREBASE})
    get_resource_service("companies").patch(COMPANY_1_ID, updates={"auth_provider": "firebase"})

    users_service = UsersAuthService()
    original_user = await users_service.get_by_email("foo@bar.com")
    assert original_user is not None

    with patch("newsroom.auth.utils.send_reset_password_email") as send_email_mock:
        resp = await client.post("/token/reset_password", form={"email": "foo@bar.com"})
        assert 302 == resp.status_code, await resp.get_data(as_text=True)
        send_email_mock.assert_called_once()
        _, token = send_email_mock.call_args.args

    with patch("newsroom.auth.views.update_firebase_password") as update_firebase_password_mock:
        resp = await client.post(
            f"/reset_password/{token}",
            form={"new_password": "newpassword", "new_password2": "newpassword"},
        )
        assert 302 == resp.status_code, await resp.get_data(as_text=True)
        update_firebase_password_mock.assert_called_once_with("foo@bar.com", "newpassword")

    updated_user = await users_service.get_by_email("foo@bar.com")
    assert updated_user is not None
    assert updated_user.token is None
    assert updated_user.token_expiry_date is None
    assert updated_user.password == original_user.password


async def test_reset_password_tokens_use_dedicated_ttl(app):
    reset_token_data = get_token_data("reset_password")
    validate_token_data = get_token_data("validate")

    reset_ttl = reset_token_data["token_expiry_date"] - utcnow()
    validate_ttl = validate_token_data["token_expiry_date"] - utcnow()

    assert reset_ttl < validate_ttl
    assert reset_ttl <= timedelta(hours=24, minutes=1)
    assert reset_ttl >= timedelta(hours=23, minutes=58)
    assert validate_ttl <= timedelta(hours=168, minutes=1)
    assert validate_ttl >= timedelta(hours=167, minutes=58)


async def test_reset_password_page_uses_target_user_locale(client, app):
    users_service = UsersAuthService()
    user = await users_service.get_by_email("foo@bar.com")
    assert user is not None

    plain_token = str(uuid4())
    token_data = get_token_data("reset_password", token=plain_token)
    await users_service.update(
        user.id,
        updates={
            "locale": "fi",
            "token": token_data["token"],
            "token_expiry_date": token_data["token_expiry_date"],
        },
    )

    locale_calls: list[tuple[str | None, str | None]] = []

    @contextmanager
    def fake_template_locale(locale=None, timezone=None):
        locale_calls.append((locale, timezone))
        yield

    with patch("newsroom.auth.views.template_locale", fake_template_locale):
        resp = await client.get(f"/reset_password/{plain_token}")
        assert 200 == resp.status_code, await resp.get_data(as_text=True)

    assert locale_calls
    assert locale_calls[0][0] == "fi"


async def test_expired_reset_password_link_shows_expiry_page(client, app):
    users_service = UsersAuthService()
    user = await users_service.get_by_email("foo@bar.com")
    assert user is not None

    plain_token = str(uuid4())
    token_data = get_token_data("reset_password", token=plain_token)
    await users_service.update(
        user.id,
        updates={
            "token": token_data["token"],
            "token_expiry_date": utcnow() - timedelta(minutes=1),
        },
    )

    resp = await client.get(f"/reset_password/{plain_token}")
    assert 200 == resp.status_code, await resp.get_data(as_text=True)
    body = await resp.get_data(as_text=True)
    assert "The link in the email has already expired" in body
