from bson import ObjectId
import pytz

from quart import json
from quart import url_for
from eve.utils import str_to_date
from datetime import datetime, timedelta
from superdesk import get_resource_service
from superdesk.utc import utcnow

from newsroom.auth import get_auth_user_by_email
from newsroom.types import User
from newsroom.utils import get_user_dict, get_company_dict, is_valid_user
from newsroom.tests.fixtures import COMPANY_1_ID
from newsroom.tests.users import ADMIN_USER_ID
from newsroom.signals import user_created, user_updated, user_deleted
from unittest import mock

from tests.utils import mock_send_email, login


async def test_user_list_fails_for_anonymous_user(app, public_user):
    async with app.test_client() as client:
        response = await client.get("/users/search")
        assert response.status_code == 302
        assert response.headers.get("location") == "/login"

    async with app.test_client() as client:
        await login(client, public_user)
        response = await client.get("/users/search")
        assert response.status_code == 403
        assert "Forbidden" in await response.get_data(as_text=True)


async def test_return_search_for_users(client, app):
    company_ids = app.data.insert("companies", [{"name": "test", "sections": {"wire": True, "agenda": True}}])

    # Register a new account
    await client.post(
        "/users/new",
        form={
            "email": "newuser@abc.org",
            "first_name": "John",
            "last_name": "Doe",
            "password": "abc",
            "phone": "1234567",
            "company": company_ids[0],
            "user_type": "public",
        },
    )

    response = await client.get("/users/search?q=jo")
    assert "John" in await response.get_data(as_text=True)
    user_data = (await response.get_json())[0]
    assert user_data.get("sections") is None


async def test_reset_password_token_sent_for_user_succeeds(app, client):
    # Insert a new user
    app.data.insert(
        "users",
        [
            {
                "_id": ObjectId("59b4c5c61d41c8d736852000"),
                "first_name": "John",
                "last_name": "Smith",
                "email": "test@sourcefabric.org",
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "user_type": "public",
                "is_validated": False,
                "is_enabled": True,
                "is_approved": False,
            }
        ],
    )
    # Resend the reset password token
    response = await client.post("/users/59b4c5c61d41c8d736852000/reset_password")
    assert response.status_code == 200
    assert '"success": true' in await response.get_data(as_text=True)
    user = get_resource_service("auth_user").find_one(req=None, email="test@sourcefabric.org")
    assert user.get("token") is not None


async def test_reset_password_token_sent_for_user_fails_for_disabled_user(app, client):
    # Insert a new user
    app.data.insert(
        "users",
        [
            {
                "_id": ObjectId("59b4c5c61d41c8d736852000"),
                "first_name": "John",
                "last_name": "Smith",
                "email": "test@sourcefabric.org",
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "user_type": "public",
                "is_validated": True,
                "is_enabled": False,
                "is_approved": False,
            }
        ],
    )
    # Resend the reset password token
    response = await client.post("/users/59b4c5c61d41c8d736852000/reset_password")
    assert response.status_code == 400
    assert '"message": "Token could not be sent"' in await response.get_data(as_text=True)
    user = get_resource_service("auth_user").find_one(req=None, email="test@sourcefabric.org")
    assert user.get("token") is None


async def test_new_user_has_correct_flags(client):
    # Register a new account
    response = await client.post(
        "/users/new",
        form={
            "email": "newuser@abc.org",
            "first_name": "John",
            "last_name": "Doe",
            "password": "abc",
            "phone": "1234567",
            "company": COMPANY_1_ID,
            "user_type": "public",
        },
    )

    assert response.status_code == 201
    user = get_resource_service("users").find_one(req=None, email="newuser@abc.org")
    assert not user["is_approved"]
    assert not user["is_enabled"]


async def test_new_user_fails_if_email_is_used_before_case_insensitive(client):
    # Register a new account
    await client.post(
        "/users/new",
        form={
            "email": "newuser@abc.org",
            "first_name": "John",
            "last_name": "Doe",
            "password": "abc",
            "phone": "1234567",
            "company": COMPANY_1_ID,
            "user_type": "public",
        },
    )

    response = await client.post(
        "/users/new",
        form={
            "email": "newUser@abc.org",
            "first_name": "John",
            "last_name": "Smith",
            "password": "abc",
            "phone": "1234567",
            "company": COMPANY_1_ID,
            "user_type": "public",
        },
    )

    assert response.status_code == 400
    assert "Email address is already in use" in await response.get_data(as_text=True)


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_create_new_user_succeeds(app, client):
    company_ids = app.data.insert(
        "companies",
        [
            {
                "phone": "2132132134",
                "sd_subscriber_id": "12345",
                "name": "Press 2 Co.",
                "is_enabled": True,
                "contact_name": "Tom",
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        # Insert a new user
        response = await client.post(
            "/users/new",
            form={
                "email": "New.User@abc.org",
                "first_name": "John",
                "last_name": "Doe",
                "password": "abc",
                "country": "Australia",
                "phone": "1234567",
                "company": company_ids[0],
                "user_type": "public",
                "is_enabled": True,
                "is_approved": True,
            },
        )
        assert response.status_code == 201
        assert len(outbox) == 1
        assert outbox[0].recipients == ["New.User@abc.org"]
        assert "account created" in outbox[0].subject

    # get reset password token
    user = get_auth_user_by_email("new.user@abc.org")
    await client.get(url_for("auth.reset_password", token=user["token"]))

    # change the password
    response = await client.post(
        url_for("auth.reset_password", token=user["token"]),
        form={
            "new_password": "abc123def",
            "new_password2": "abc123def",
        },
    )
    assert response.status_code == 302

    # Login with the new account succeeds
    response = await login(client, {"email": "new.user@abc.org", "password": "abc123def"}, follow_redirects=True)
    assert response.status_code == 200
    assert "John" in await response.get_data(as_text=True)

    # Logout
    response = await client.get(url_for("auth.logout"), follow_redirects=True)
    txt = await response.get_data(as_text=True)
    assert "John" not in txt
    assert "Login" in txt


async def test_new_user_fails_if_fields_not_provided(client):
    # Register a new account
    response = await client.post(
        url_for("users.create"),
        form={
            "phone": "1234567",
        },
    )
    assert response.status_code == 400
    errors = await response.get_json()

    for name in ["first_name", "last_name", "email"]:
        assert "required" in errors[name][0], name

    assert errors["user_type"][0] == "Not a valid choice."


async def test_new_user_can_be_deleted(client):
    # Register a new account
    response = await client.post(
        "/users/new",
        form={
            "email": "newuser@abc.org",
            "first_name": "John",
            "last_name": "Doe",
            "password": "abc",
            "phone": "1234567",
            "company": COMPANY_1_ID,
            "user_type": "public",
        },
    )

    # print(response.get_data(as_text=True))

    assert response.status_code == 201
    user = get_resource_service("users").find_one(req=None, email="newuser@abc.org")

    response = await client.delete("/users/{}".format(user["_id"]))
    assert response.status_code == 200

    user = get_resource_service("users").find_one(req=None, email="newuser@abc.org")
    assert user is None


async def test_return_search_for_all_users(client, app):
    for i in range(250):
        app.data.insert(
            "users",
            [
                {
                    "email": "foo%s@bar.com" % i,
                    "first_name": "Foo%s" % i,
                    "is_enabled": True,
                    "receive_email": True,
                    "company": "",
                }
            ],
        )

    resp = await client.get("/users/search?q=fo")
    data = json.loads(await resp.get_data())
    assert 250 <= len(data)


async def test_active_user(client, app):
    resp = await client.get("/users/search?q=admin")
    data = json.loads(await resp.get_data())
    assert data[0].get("last_active")


async def test_active_users_and_active_companies(client, app):
    app.data.insert(
        "users",
        [
            {
                "_id": "1",
                "email": "foo1@bar.com",
                "last_name": "bar1",
                "first_name": "foo1",
                "user_type": "public",
                "is_approved": True,
                "is_enabled": True,
                "is_validated": True,
                "company": "1",
            },
            {
                "_id": "2",
                "email": "foo2@bar.com",
                "last_name": "bar2",
                "first_name": "foo2",
                "user_type": "public",
                "is_approved": True,
                "is_enabled": False,
                "is_validated": True,
                "company": "1",
            },
            {
                "_id": "3",
                "email": "foo3@bar.com",
                "last_name": "bar3",
                "first_name": "foo3",
                "user_type": "administrator",
                "is_approved": True,
                "is_enabled": True,
                "is_validated": True,
                "company": "2",
            },
            {
                "_id": "4",
                "email": "foo4@bar.com",
                "last_name": "bar4",
                "first_name": "foo4",
                "user_type": "administrator",
                "is_approved": True,
                "is_enabled": True,
                "is_validated": True,
                "company": "3",
            },
        ],
    )

    app.data.insert(
        "companies",
        [
            {"_id": "1", "name": "Company1", "is_enabled": True},
            {"_id": "2", "name": "Company2", "is_enabled": False},
            {
                "_id": "3",
                "name": "Company3",
                "is_enabled": True,
                "expiry_date": datetime.utcnow() - timedelta(days=1),
            },
        ],
    )

    async with app.test_request_context("/"):
        users = get_user_dict()
        companies = get_company_dict()

        assert "1" in users
        assert "2" not in users
        assert "3" not in users

        assert "1" in companies
        assert "2" not in companies


async def test_expired_company_does_not_restrict_activity(client, app):
    app.data.insert(
        "companies",
        [
            {"_id": "1", "name": "Company1", "is_enabled": True},
            {"_id": "2", "name": "Company2", "is_enabled": False},
            {
                "_id": "3",
                "name": "Company3",
                "is_enabled": True,
                "expiry_date": datetime.utcnow() - timedelta(days=1),
            },
        ],
    )

    async with app.test_request_context("/"):
        companies = get_company_dict()

        assert "1" in companies
        assert "2" not in companies
        assert "3" not in companies

        app.config["ALLOW_EXPIRED_COMPANY_LOGINS"] = True
        companies = get_company_dict()

        assert "1" in companies
        assert "2" not in companies
        assert "3" in companies


async def test_is_valid_user(client, app):
    users = [
        {
            "email": "foo1@bar.com",
            "last_name": "bar1",
            "first_name": "foo1",
            "user_type": "public",
            "is_approved": True,
            "is_enabled": True,
            "is_validated": True,
            "company": "1",
        },
        {
            "email": "foo2@bar.com",
            "last_name": "bar2",
            "first_name": "foo2",
            "user_type": "public",
            "is_approved": True,
            "is_enabled": False,
            "is_validated": True,
            "company": "1",
        },
        {
            "email": "foo3@bar.com",
            "last_name": "bar3",
            "first_name": "foo3",
            "user_type": "administrator",
            "is_approved": True,
            "is_enabled": True,
            "is_validated": True,
            "company": "2",
        },
        {
            "email": "foo4@bar.com",
            "last_name": "bar4",
            "first_name": "foo4",
            "user_type": "administrator",
            "is_approved": True,
            "is_enabled": True,
            "is_validated": True,
            "company": "3",
        },
    ]

    companies = [
        {"_id": "1", "name": "Enabled", "is_enabled": True},
        {"_id": "2", "name": "Not Enabled", "is_enabled": False},
        {"_id": "3", "name": "Expired", "is_enabled": True, "expiry_date": datetime.utcnow() - timedelta(days=1)},
    ]

    async with app.test_request_context("/"):
        assert await is_valid_user(users[0], companies[0]) is True
        assert await is_valid_user(users[1], companies[0]) is False
        assert await is_valid_user(users[2], companies[1]) is False
        assert await is_valid_user(users[3], companies[2]) is False


async def test_account_manager_can_update_user(app, client):
    company_ids = app.data.insert(
        "companies",
        [
            {
                "phone": "2132132134",
                "sd_subscriber_id": "12345",
                "name": "Press 2 Co.",
                "is_enabled": True,
                "contact_name": "Tom",
            }
        ],
    )
    account_mgr = {
        "_id": ObjectId("5c5914275f627d5885fee6a8"),
        "first_name": "Account",
        "last_name": "Manager",
        "email": "accountmgr@sourcefabric.org",
        "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
        "user_type": "account_management",
        "is_validated": True,
        "is_enabled": True,
        "is_approved": True,
        "receive_email": True,
        "phone": "2132132134",
        "company": company_ids[0],
    }
    app.data.insert("users", [account_mgr])
    response = await login(client, {"email": "accountmgr@sourcefabric.org", "password": "admin"}, follow_redirects=True)
    assert response.status_code == 200
    account_mgr["first_name"] = "Updated Account"
    response = await client.post("users/5c5914275f627d5885fee6a8", form=account_mgr, follow_redirects=True)
    assert response.status_code == 200
    # account manager can't promote themselves
    account_mgr["user_type"] = "administrator"
    response = await client.post("users/5c5914275f627d5885fee6a8", form=account_mgr, follow_redirects=True)
    assert response.status_code == 401


async def test_signals(client, app):
    created_listener = mock.Mock(return_value=None)
    updated_listener = mock.Mock(return_value=None)
    deleted_listener = mock.Mock(return_value=None)

    # use weak to fix issue with weak ref and mock
    user_created.connect(created_listener, weak=False)
    user_updated.connect(updated_listener, weak=False)
    user_deleted.connect(deleted_listener, weak=False)

    user = {
        "email": "foo1@bar.com",
        "last_name": "bar1",
        "first_name": "foo1",
        "user_type": "public",
        "company": ObjectId("59b4c5c61d41c8d736852fbf"),
    }

    resp = await client.post(
        "/users/new",
        form=user,
    )
    assert resp.status_code == 201, await resp.get_data(as_text=True)

    created_listener.assert_called_once()
    assert "_id" in created_listener.call_args.kwargs["user"]
    assert user["email"] == created_listener.call_args.kwargs["user"]["email"]

    user["email"] = "foo@example.com"
    user["is_enabled"] = True
    user_id = created_listener.call_args.kwargs["user"]["_id"]
    resp = await client.post(
        f"/users/{user_id}",
        form=user,
    )
    assert resp.status_code == 200, await resp.get_data(as_text=True)

    updated_listener.assert_called_once()
    assert user_id == updated_listener.call_args.kwargs["user"]["_id"]
    assert user["email"] == updated_listener.call_args.kwargs["user"]["email"]
    updated_listener.reset_mock()

    token = app.data.find_one("auth_user", req=None, _id=user_id)["token"]

    resp = await client.get(f"/validate/{token}")
    assert 302 == resp.status_code, await resp.get_data(as_text=True)
    updated_listener.assert_called_once()
    updated_listener.reset_mock()

    with mock.patch("newsroom.auth.utils.send_reset_password_email", autospec=True) as password_email:
        resp = await client.post(f"/users/{user_id}/reset_password")
        assert 200 == resp.status_code, await resp.get_data(as_text=True)
        password_email.assert_called_once()
        reset_token = password_email.call_args.args[1]
        assert reset_token

    updated_listener.reset_mock()
    resp = await client.post(
        f"/reset_password/{reset_token}", form={"new_password": "newpassword123", "new_password2": "newpassword123"}
    )
    assert 302 == resp.status_code, await resp.get_data(as_text=True)
    updated_listener.assert_called_once()

    resp = await client.delete(
        f"/users/{user_id}",
    )
    assert resp.status_code == 200, await resp.get_data(as_text=True)

    deleted_listener.assert_called_once()
    assert user_id == deleted_listener.call_args.kwargs["user"]["_id"]
    assert user["email"] == deleted_listener.call_args.kwargs["user"]["email"]


async def test_user_can_update_notification_schedule(app, client):
    async def update_user_schedule(data):
        response = await client.post(
            f"/users/{ADMIN_USER_ID}/notification_schedules",
            json=data,
        )
        assert response.status_code == 200

    # Start out with an undefined notification schedule
    user = await (await client.get(f"/users/{ADMIN_USER_ID}")).get_json()
    user["_id"] = ObjectId(user["_id"])
    assert user.get("notification_schedule") is None

    # Now update the schedule with timezone and times
    await update_user_schedule({"timezone": "Australia/Sydney", "times": ["08:00", "16:00", "20:00"]})
    user = await (await client.get(f"/users/{ADMIN_USER_ID}")).get_json()
    user["_id"] = ObjectId(user["_id"])
    assert user["notification_schedule"]["timezone"] == "Australia/Sydney"
    assert user["notification_schedule"]["times"] == ["08:00", "16:00", "20:00"]
    assert user["notification_schedule"].get("last_run_time") is None

    # Update the schedules ``last_run_time``
    now = utcnow()
    get_resource_service("users").update_notification_schedule_run_time(user, now)
    user = await (await client.get(f"/users/{ADMIN_USER_ID}")).get_json()
    assert user["notification_schedule"]["timezone"] == "Australia/Sydney"
    assert user["notification_schedule"]["times"] == ["08:00", "16:00", "20:00"]
    assert str_to_date(user["notification_schedule"]["last_run_time"]).replace(tzinfo=pytz.utc) == now

    # Update the schedule's timezone and times
    await update_user_schedule({"timezone": "Europe/Prague", "times": ["09:00", "17:00", "21:00"]})
    user = await (await client.get(f"/users/{ADMIN_USER_ID}")).get_json()
    user["_id"] = ObjectId(user["_id"])
    # Make sure all attributes were retained, specifically the ``last_run_time``
    assert user["notification_schedule"]["timezone"] == "Europe/Prague"
    assert user["notification_schedule"]["times"] == ["09:00", "17:00", "21:00"]
    assert str_to_date(user["notification_schedule"]["last_run_time"]).replace(tzinfo=pytz.utc) == now


async def test_check_etag_when_updating_user(client):
    # Register a new account
    await client.post(
        "/users/new",
        form={
            "email": "newuser@abc.org",
            "first_name": "John",
            "last_name": "Doe",
            "password": "abc",
            "phone": "1234567",
            "company": ObjectId("59b4c5c61d41c8d736852fbf"),
            "user_type": "public",
            "sections": "wire,agenda",
        },
    )

    response = await client.get("/users/search?q=jo")
    assert "John" in await response.get_data(as_text=True)

    user_data = (await response.get_json())[0]
    patch_data = user_data.copy()
    patch_data["sections"] = "wire,agenda"
    patch_data["first_name"] = "Foo"

    response = await client.post(
        f"/users/{user_data['_id']}", form=patch_data, headers={"If-Match": "something random"}
    )

    assert response.status_code == 412

    response = await client.post(
        f"/users/{user_data['_id']}",
        form=patch_data,
        headers={"If-Match": user_data["_etag"]},
    )

    assert response.status_code == 200


async def test_create_user_inherit_sections(app):
    company_ids = app.data.insert("companies", [{"name": "test", "sections": {"agenda": True, "wire": False}}])
    assert company_ids
    user_ids = app.data.insert("users", [{"email": "newuser@example.com", "company": company_ids[0]}])
    assert user_ids
    user = app.data.find_one("users", req=None, _id=user_ids[0])
    assert user.get("sections") is None  # When sections has a `Falsy` value, the parent Company sections will be used


async def test_filter_and_sorting_user(app, client):
    users = await (await client.get("/users/search?q=")).get_json()
    assert len(users) == 3
    response = await client.get("/users/search?q=admin")
    assert "admin" in await response.get_data(as_text=True)
    user_data = (await response.get_json())[0]
    patch_data = user_data.copy()
    patch_data["first_name"] = "Zoe"
    patch_data["last_name"] = "AAba"
    response = await client.post(
        f"/users/{user_data['_id']}",
        form=patch_data,
        headers={"If-Match": user_data["_etag"]},
    )
    assert response.status_code == 200

    # sort by First_name
    users = await (await client.get("/users/search?q=&sort=[('first_name', 1)]")).get_json()
    assert users[0]["first_name"] == "Foo"
    assert users[2]["first_name"] == "Zoe"

    # sort by Last_name
    users = await (await client.get("/users/search?q=&sort=[('last_name', 1)]")).get_json()
    assert users[0]["last_name"] == "AAba"
    assert users[1]["last_name"] == "Bar"

    # filter by Company_id
    users = await (await client.get('/users/search?q=&where={"company":"6215cbf55fc14ebe18e175a5"}')).get_json()
    assert len(users) == 2
    assert users[0]["company"] == "6215cbf55fc14ebe18e175a5"

    # filter by company and search by name
    users = await (await client.get('/users/search?q=foo&where={"company":"6215cbf55fc14ebe18e175a5"}')).get_json()
    assert len(users) == 1

    # filter by products
    users = await (await client.get('/users/search?q=&where={"products._id":"random"}')).get_json()
    assert len(users) == 0


async def test_user_has_paused_notifications(app):
    user = User(email="foo", user_type="public")
    assert not get_resource_service("users").user_has_paused_notifications(user)

    user["notification_schedule"] = {"pause_from": "2024-01-01", "pause_to": "2024-01-01"}
    assert not get_resource_service("users").user_has_paused_notifications(user)

    user["notification_schedule"] = {"pause_from": "2024-01-01", "pause_to": "2050-01-01"}
    assert get_resource_service("users").user_has_paused_notifications(user)
