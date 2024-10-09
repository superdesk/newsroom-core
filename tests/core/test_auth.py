import datetime
from quart import url_for
from bson import ObjectId
from pytest import fixture
from newsroom.users.service import UsersService
from superdesk.utils import get_hash

from newsroom.auth.token import verify_auth_token
from newsroom.auth.views import _is_password_valid
from newsroom.tests.users import ADMIN_USER_EMAIL
from newsroom.companies import CompanyServiceAsync
from tests.utils import get_user_by_email, login, logout

disabled_company = ObjectId()
expired_company = ObjectId()
company = ObjectId()


@fixture(autouse=True)
async def init(app):
    app.data.insert(
        "companies",
        [
            {
                "_id": disabled_company,
                "name": "Press 2 co.",
                "is_enabled": False,
            },
            {
                "_id": expired_company,
                "name": "Company co.",
                "is_enabled": True,
                "expiry_date": datetime.datetime.now() - datetime.timedelta(days=5),
            },
            {"_id": company, "name": "Foo bar co.", "is_enabled": True},
        ],
    )


async def test_login_fails_for_wrong_username_or_password(client):
    response = await login(client, {"email": "xyz@abc.org", "password": "abc"}, assert_login=False)
    assert "Invalid username or password" in await response.get_data(as_text=True)


async def test_login_fails_for_disabled_user(app, client):
    # Register a new account
    app.data.insert(
        "users",
        [
            {
                "_id": ObjectId(),
                "first_name": "test",
                "last_name": "test",
                "email": "test@sourcefabric.org",
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "user_type": "public",
                "is_validated": True,
                "is_enabled": False,
                "is_approved": True,
                "company": company,
                "_created": datetime.datetime(2016, 4, 26, 13, 0, 33, tzinfo=datetime.timezone.utc),
            }
        ],
    )

    response = await login(client, {"email": "test@sourcefabric.org", "password": "admin"}, assert_login=False)
    assert "Account is disabled" in await response.get_data(as_text=True)


async def test_login_fails_for_user_with_disabled_company(app, client):
    # Register a new account
    app.data.insert(
        "users",
        [
            {
                "_id": ObjectId(),
                "first_name": "test",
                "last_name": "test",
                "email": "test@sourcefabric.org",
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "user_type": "public",
                "company": disabled_company,
                "is_enabled": True,
                "is_approved": True,
                "is_validated": True,
                "_created": datetime.datetime(2016, 4, 26, 13, 0, 33, tzinfo=datetime.timezone.utc),
            }
        ],
    )

    response = await login(client, {"email": "test@sourcefabric.org", "password": "admin"}, assert_login=False)
    assert "Company account has been disabled" in await response.get_data(as_text=True)


async def test_login_succesfull_for_user_with_expired_company(app, client):
    # Register a new account
    app.data.insert(
        "users",
        [
            {
                "_id": ObjectId(),
                "first_name": "test",
                "last_name": "test",
                "email": "test@sourcefabric.org",
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "user_type": "public",
                "company": expired_company,
                "is_validated": True,
                "is_enabled": True,
                "_created": datetime.datetime(2016, 4, 26, 13, 0, 33, tzinfo=datetime.timezone.utc),
            }
        ],
    )

    response = await client.post(
        url_for("auth.login"),
        form={"email": "test@sourcefabric.org", "password": "admin"},
        follow_redirects=True,
    )
    assert "test" in await response.get_data(as_text=True)


async def test_login_for_user_with_enabled_company_succeeds(app, client):
    # Register a new account
    app.data.insert(
        "users",
        [
            {
                "_id": ObjectId(),
                "first_name": "John",
                "last_name": "Doe",
                "email": "test@sourcefabric.org",
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "user_type": "public",
                "company": disabled_company,
                "is_validated": True,
                "is_approved": True,
                "is_enabled": True,
                "_created": datetime.datetime(2016, 4, 26, 13, 0, 33, tzinfo=datetime.timezone.utc),
            }
        ],
    )

    await CompanyServiceAsync().update(disabled_company, updates={"is_enabled": True})
    response = await login(client, {"email": "test@sourcefabric.org", "password": "admin"}, follow_redirects=True)
    assert "John" in await response.get_data(as_text=True)


async def test_login_fails_for_not_approved_user(app, client):
    # If user is created more than 14 days ago login fails
    app.data.insert(
        "users",
        [
            {
                "_id": ObjectId(),
                "first_name": "test",
                "last_name": "test",
                "email": "test@sourcefabric.org",
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "user_type": "public",
                "is_validated": True,
                "is_enabled": True,
                "company": company,
                "is_approved": False,
                "_created": datetime.datetime(2016, 4, 26, 13, 0, 33, tzinfo=datetime.timezone.utc),
            }
        ],
    )
    response = await login(client, {"email": "test@sourcefabric.org", "password": "admin"}, follow_redirects=True)
    assert "Account has not been approved" in await response.get_data(as_text=True)


async def test_login_fails_for_many_times_gets_limited(client, app):
    for i in range(1, 100):
        response = await client.post(
            url_for("auth.login"),
            form={"email": "xyz{}@abc.org".format(i), "password": "abc"},
            follow_redirects=True,
        )
        if response.status_code == 429:
            break
    else:
        assert False, "Ratelimit not set"


async def test_account_is_locked_after_5_wrong_passwords(app, client):
    await logout(client)
    # Register a new account
    app.data.insert(
        "users",
        [
            {
                "_id": ObjectId(),
                "first_name": "John",
                "last_name": "Doe",
                "email": "test@sourcefabric.org",
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "user_type": "public",
                "company": company,
                "is_validated": True,
                "is_approved": True,
                "is_enabled": True,
                "_created": datetime.datetime(2016, 4, 26, 13, 0, 33, tzinfo=datetime.timezone.utc),
            }
        ],
    )
    for i in range(1, 10):
        response = await login(
            client,
            {"email": "test@sourcefabric.org", "password": "wrongone"},
            assert_login=False,
            follow_redirects=True,
            auto_logout=False,
        )
        if i <= 5:
            assert "Invalid username or password" in await response.get_data(as_text=True)
        else:
            assert "Your account has been locked" in await response.get_data(as_text=True)
            break

    # get the user
    user = await get_user_by_email("test@sourcefabric.org")
    assert user["is_enabled"] is False


async def test_account_stays_unlocked_after_few_wrong_attempts(app, client):
    await logout(client)
    # Register a new account
    app.data.insert(
        "users",
        [
            {
                "_id": ObjectId(),
                "first_name": "John",
                "last_name": "Doe",
                "email": "test@sourcefabric.org",
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "user_type": "public",
                "company": company,
                "is_validated": True,
                "is_approved": True,
                "is_enabled": True,
                "_created": datetime.datetime(2016, 4, 26, 13, 0, 33, tzinfo=datetime.timezone.utc),
            }
        ],
    )
    for i in range(1, 4):
        response = await login(
            client,
            {"email": "test@sourcefabric.org", "password": "wrongone"},
            assert_login=False,
            follow_redirects=True,
        )
        if i <= 5:
            assert "Invalid username or password" in await response.get_data(as_text=True)

    # correct login will clear the attempt count
    await login(client, {"email": "test@sourcefabric.org", "password": "admin"}, follow_redirects=True)

    # now logout
    await logout(client)

    # user can try 4 more times
    for i in range(1, 4):
        response = await login(
            client,
            {"email": "test@sourcefabric.org", "password": "wrongone"},
            assert_login=False,
            follow_redirects=True,
        )
        if i <= 5:
            assert "Invalid username or password" in await response.get_data(as_text=True)

    # get the user
    user = await get_user_by_email("test@sourcefabric.org")
    assert user["is_enabled"] is True


async def test_account_appears_locked_for_non_existing_user(client):
    await logout(client)
    for i in range(1, 10):
        response = await login(
            client,
            {"email": "xyz@abc.org", "password": "abc"},
            auto_logout=False,
            follow_redirects=True,
            assert_login=False,
        )
        if i <= 5:
            assert "Invalid username or password" in await response.get_data(as_text=True)
        else:
            assert "Your account has been locked" in await response.get_data(as_text=True)


async def test_login_with_remember_me_selected_creates_permanent_session(app, client):
    # Register a new account
    app.data.insert(
        "users",
        [
            {
                "_id": ObjectId(),
                "first_name": "John",
                "last_name": "Doe",
                "email": "test@sourcefabric.org",
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "user_type": "public",
                "company": company,
                "is_validated": True,
                "is_approved": True,
                "is_enabled": True,
                "_created": datetime.datetime(2016, 4, 26, 13, 0, 33, tzinfo=datetime.timezone.utc),
            }
        ],
    )

    # login with remember_me = None
    await client.post(
        url_for("auth.login"),
        form={"email": "test@sourcefabric.org", "password": "admin"},
        follow_redirects=True,
    )

    async with client.session_transaction() as session:
        assert session.permanent is False

    # now logout
    await client.get(url_for("auth.logout"), follow_redirects=True)

    # login with remember_me = True
    await client.post(
        url_for("auth.login"),
        form={
            "email": "test@sourcefabric.org",
            "password": "admin",
            "remember_me": True,
        },
        follow_redirects=True,
    )

    async with client.session_transaction() as session:
        assert session.permanent is True


async def test_login_token_fails_for_wrong_username_or_password(client):
    response = await client.post(
        url_for("auth.get_login_token"),
        form={"email": "xyz@abc.org", "password": "abc"},
    )
    assert "Invalid username or password" in await response.get_data(as_text=True)


async def test_login_token_succeeds_for_correct_username_or_password(client):
    response = await client.post(
        url_for("auth.get_login_token"),
        form={"email": "admin@sourcefabric.org", "password": "admin"},
    )
    token = await response.get_data(as_text=True)
    data = verify_auth_token(token)
    assert data is not None
    assert data["first_name"] == "admin"
    assert data["last_name"] == "admin"
    assert data["user_type"] == "administrator"


async def test_login_with_token_fails_for_wrong_token(client):
    response = await client.get("/login/token/1234")
    assert "Invalid token" in await response.get_data(as_text=True)


async def test_login_with_token_succeeds_for_correct_token(client):
    response = await client.post(
        url_for("auth.get_login_token"),
        form={"email": "admin@sourcefabric.org", "password": "admin"},
    )
    token = await response.get_data(as_text=True)
    await client.get("/login/token/{}".format(token), follow_redirects=True)

    async with client.session_transaction() as session:
        assert session["user_type"] == "administrator"


async def test_is_user_valid_empty_password():
    password = "foo".encode("utf-8")
    assert not _is_password_valid(password, {"_id": "foo", "email": "foo@example.com"})
    assert not _is_password_valid(password, {"_id": "foo", "email": "foo@example.com", "password": None})
    assert not _is_password_valid(password, {"_id": "foo", "email": "foo@example.com", "password": ""})
    assert _is_password_valid(
        password,
        {"_id": "foo", "email": "foo@example.com", "password": get_hash("foo", 10)},
    )


async def test_login_for_public_user_if_company_not_assigned(client, app):
    app.data.insert(
        "users",
        [
            {
                "_id": ObjectId(),
                "first_name": "test",
                "last_name": "test",
                "email": "test@sourcefabric.org",
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "user_type": "public",
                "is_validated": True,
                "is_enabled": True,
                "is_approved": True,
                "_created": datetime.datetime(2016, 4, 26, 13, 0, 33, tzinfo=datetime.timezone.utc),
            }
        ],
    )

    response = await login(client, {"email": "test@sourcefabric.org", "password": "admin"}, follow_redirects=True)
    assert "Insufficient Permissions. Access denied." in await response.get_data(as_text=True)


async def test_login_for_internal_user_if_company_not_assigned(client, app):
    app.data.insert(
        "users",
        [
            {
                "_id": ObjectId(),
                "first_name": "test",
                "last_name": "test",
                "email": "test@sourcefabric.org",
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "user_type": "internal",
                "is_validated": True,
                "is_enabled": True,
                "is_approved": True,
                "_created": datetime.datetime(2016, 4, 26, 13, 0, 33, tzinfo=datetime.timezone.utc),
            }
        ],
    )

    response = await login(client, {"email": "test@sourcefabric.org", "password": "admin"}, follow_redirects=True)
    assert "Insufficient Permissions. Access denied." in await response.get_data(as_text=True)


async def test_access_for_disabled_user(app, client):
    # Register a new account
    user_id = ObjectId()
    app.data.insert(
        "users",
        [
            {
                "_id": user_id,
                "first_name": "test",
                "last_name": "test",
                "email": "test@sourcefabric.org",
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "user_type": "administrator",
                "phone": "123456",
                "is_validated": True,
                "is_enabled": True,
                "is_approved": True,
                "company": company,
                "_created": datetime.datetime(2016, 4, 26, 13, 0, 33, tzinfo=datetime.timezone.utc),
            }
        ],
    )

    user_entry = await UsersService().find_by_id(user_id)
    assert user_entry is not None

    user = user_entry.to_dict()

    await login(client, {"email": "test@sourcefabric.org"})
    resp = await client.get("/bookmarks_wire")
    assert 200 == resp.status_code

    await login(client, {"email": ADMIN_USER_EMAIL})
    resp = await client.post(
        "/users/{}".format(user_id),
        form={
            "_id": user_id,
            "first_name": "test test",
            "last_name": "test1",
            "email": "test@sourcefabric.org",
            "user_type": "administrator",
            "phone": "1234567",
            "is_validated": "true",
            "is_enabled": "false",
            "is_approved": "true",
            "company": company,
            "_etag": user.get("_etag"),
        },
    )
    assert 200 == resp.status_code

    resp = await login(client, {"email": "test@sourcefabric.org"}, assert_login=False)
    assert "Account is disabled" in await resp.get_data(as_text=True)

    resp = await client.get("/users/search")
    assert 302 == resp.status_code

    resp = await client.get("/wire")
    assert 302 == resp.status_code


async def test_access_for_disabled_company(app, client):
    # Register a new account
    user_id = ObjectId()
    app.data.insert(
        "users",
        [
            {
                "_id": user_id,
                "first_name": "test",
                "last_name": "test",
                "email": "test@sourcefabric.org",
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "user_type": "administrator",
                "phone": "123456",
                "is_validated": True,
                "is_enabled": True,
                "is_approved": True,
                "company": disabled_company,
                "_created": datetime.datetime(2016, 4, 26, 13, 0, 33, tzinfo=datetime.timezone.utc),
            }
        ],
    )

    async with client.session_transaction() as session:
        session["user"] = str(user_id)
        session["user_type"] = "administrator"
        session["name"] = "public"
        session["auth_ttl"] = None
    resp = await client.get("/bookmarks_wire")
    assert 302 == resp.status_code


async def test_access_for_not_approved_user(client, app):
    user_ids = app.data.insert(
        "users",
        [
            {
                "email": "foo2@bar.com",
                "first_name": "Foo",
                "is_enabled": True,
                "is_approved": False,
                "receive_email": True,
                "user_type": "administrator",
                "_created": datetime.datetime(2016, 4, 26, 13, 0, 33, tzinfo=datetime.timezone.utc),
            }
        ],
    )

    async with client.session_transaction() as session:
        user = str(user_ids[0])
        session["user"] = user
        session["user_type"] = "administrator"
        session["auth_ttl"] = None
    resp = await client.post(
        "/users/%s/topics" % user,
        json={"label": "bar", "query": "test", "notifications": True, "topic_type": "wire"},
    )
    assert 302 == resp.status_code, await resp.get_data()


async def test_change_password(client, admin):
    await login(client, admin)
    resp = await client.get("/change_password")
    assert 200 == resp.status_code

    resp = await client.post(
        "/change_password",
        form={
            "old_password": "foo",
            "new_password": "newpassword",
            "new_password2": "newpassword",
        },
        follow_redirects=True,
    )

    assert 200 == resp.status_code
    assert "Current password invalid" in await resp.get_data(as_text=True)

    resp = await client.post(
        "/change_password",
        form={
            "old_password": "admin",
            "new_password": "newpassword",
            "new_password2": "newpassword",
        },
        follow_redirects=True,
    )

    assert 200 == resp.status_code
    assert "Your password has been changed" in await resp.get_data(as_text=True)
