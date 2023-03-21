from bson import ObjectId
from flask import json
from flask import url_for
from datetime import datetime, timedelta
from superdesk import get_resource_service

from newsroom.auth import get_user_by_email
from newsroom.utils import get_user_dict, get_company_dict, is_valid_user
from newsroom.tests.fixtures import COMPANY_1_ID
from newsroom.signals import user_created, user_updated, user_deleted
from unittest import mock

from tests.utils import mock_send_email


def test_user_list_fails_for_anonymous_user(client, anonymous_user):
    response = client.get("/users/search")
    assert response.status_code == 403
    assert b"Forbidden" in response.data


def test_return_search_for_users(client):
    # Register a new account
    response = client.post(
        "/users/new",
        data={
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

    response = client.get("/users/search?q=jo")
    assert "John" in response.get_data(as_text=True)
    user_data = response.get_json()[0]
    assert user_data["sections"]["agenda"]
    assert user_data["sections"]["wire"]


def test_reset_password_token_sent_for_user_succeeds(app, client):
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
    response = client.post("/users/59b4c5c61d41c8d736852000/reset_password")
    assert response.status_code == 200
    assert '"success": true' in response.get_data(as_text=True)
    user = get_resource_service("users").find_one(req=None, email="test@sourcefabric.org")
    assert user.get("token") is not None


def test_reset_password_token_sent_for_user_fails_for_disabled_user(app, client):
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
    response = client.post("/users/59b4c5c61d41c8d736852000/reset_password")
    assert response.status_code == 400
    assert '"message": "Token could not be sent"' in response.get_data(as_text=True)
    user = get_resource_service("users").find_one(req=None, email="test@sourcefabric.org")
    assert user.get("token") is None


def test_new_user_has_correct_flags(client):
    # Register a new account
    response = client.post(
        "/users/new",
        data={
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
    assert not user["is_approved"]
    assert not user["is_enabled"]


def test_new_user_fails_if_email_is_used_before_case_insensitive(client):
    # Register a new account
    response = client.post(
        "/users/new",
        data={
            "email": "newuser@abc.org",
            "first_name": "John",
            "last_name": "Doe",
            "password": "abc",
            "phone": "1234567",
            "company": COMPANY_1_ID,
            "user_type": "public",
        },
    )

    response = client.post(
        "/users/new",
        data={
            "email": "newUser@abc.org",
            "first_name": "John",
            "last_name": "Smith",
            "password": "abc",
            "phone": "1234567",
            "company": COMPANY_1_ID,
            "user_type": "public",
        },
    )

    # print(response.get_data(as_text=True))

    assert response.status_code == 400
    assert "Email address is already in use" in response.get_data(as_text=True)


@mock.patch("newsroom.email.send_email", mock_send_email)
def test_create_new_user_succeeds(app, client):
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
        response = client.post(
            "/users/new",
            data={
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
    user = get_user_by_email("new.user@abc.org")
    client.get(url_for("auth.reset_password", token=user["token"]))

    # change the password
    response = client.post(
        url_for("auth.reset_password", token=user["token"]),
        data={
            "new_password": "abc123def",
            "new_password2": "abc123def",
        },
    )
    assert response.status_code == 302

    # Login with the new account succeeds
    response = client.post(
        url_for("auth.login"),
        data={"email": "new.user@abc.org", "password": "abc123def"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "John" in response.get_data(as_text=True)

    # Logout
    response = client.get(url_for("auth.logout"), follow_redirects=True)
    txt = response.get_data(as_text=True)
    assert "John" not in txt
    assert "Login" in txt


def test_new_user_fails_if_fields_not_provided(client):
    # Register a new account
    response = client.post(
        url_for("users.create"),
        data={
            "phone": "1234567",
        },
    )
    txt = response.get_data(as_text=True)

    # print(txt)

    assert '"first_name"' in txt
    assert '"last_name"' in txt
    assert '"email"' in txt
    assert "user_type" in txt


def test_new_user_can_be_deleted(client):
    # Register a new account
    response = client.post(
        "/users/new",
        data={
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

    response = client.delete("/users/{}".format(user["_id"]))
    assert response.status_code == 200

    user = get_resource_service("users").find_one(req=None, email="newuser@abc.org")
    assert user is None


def test_return_search_for_all_users(client, app):
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

    resp = client.get("/users/search?q=fo")
    data = json.loads(resp.get_data())
    assert 250 <= len(data)


def test_active_user(client, app):
    resp = client.get("/users/search?q=admin")
    data = json.loads(resp.get_data())
    assert data[0].get("last_active")


def test_active_users_and_active_companies(client, app):
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

    with app.test_request_context():
        users = get_user_dict()
        companies = get_company_dict()

        assert "1" in users
        assert "2" not in users
        assert "3" not in users

        assert "1" in companies
        assert "2" not in companies


def test_expired_company_does_not_restrict_activity(client, app):
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

    with app.test_request_context():
        companies = get_company_dict()

        assert "1" in companies
        assert "2" not in companies
        assert "3" not in companies

        app.config["ALLOW_EXPIRED_COMPANY_LOGINS"] = True
        companies = get_company_dict()

        assert "1" in companies
        assert "2" not in companies
        assert "3" in companies


def test_is_valid_user(client, app):
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

    with app.test_request_context():
        assert is_valid_user(users[0], companies[0]) is True
        assert is_valid_user(users[1], companies[0]) is False
        assert is_valid_user(users[2], companies[1]) is False
        assert is_valid_user(users[3], companies[2]) is False


def test_account_manager_can_update_user(app, client):
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
    response = client.post(
        url_for("auth.login"),
        data={"email": "accountmgr@sourcefabric.org", "password": "admin"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    account_mgr["first_name"] = "Updated Account"
    response = client.post("users/5c5914275f627d5885fee6a8", data=account_mgr, follow_redirects=True)
    assert response.status_code == 200
    # account manager can't promote themselves
    account_mgr["user_type"] = "administrator"
    response = client.post("users/5c5914275f627d5885fee6a8", data=account_mgr, follow_redirects=True)
    assert response.status_code == 401


def test_signals(client, app):
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

    resp = client.post(
        "/users/new",
        data=user,
    )
    assert resp.status_code == 201, resp.get_data(as_text=True)

    created_listener.assert_called_once()
    assert "_id" in created_listener.call_args.kwargs["user"]
    assert user["email"] == created_listener.call_args.kwargs["user"]["email"]

    user["email"] = "foo@example.com"
    user["is_enabled"] = True
    user_id = created_listener.call_args.kwargs["user"]["_id"]
    resp = client.post(
        f"/users/{user_id}",
        data=user,
    )
    assert resp.status_code == 200, resp.get_data(as_text=True)

    updated_listener.assert_called_once()
    assert user_id == updated_listener.call_args.kwargs["user"]["_id"]
    assert user["email"] == updated_listener.call_args.kwargs["user"]["email"]
    updated_listener.reset_mock()

    token = app.data.find_one("users", req=None, _id=user_id)["token"]

    resp = client.get(f"/validate/{token}")
    assert 302 == resp.status_code, resp.get_data(as_text=True)
    updated_listener.assert_called_once()
    updated_listener.reset_mock()

    with mock.patch("newsroom.auth.utils.send_reset_password_email", autospec=True) as password_email:
        resp = client.post(f"/users/{user_id}/reset_password")
        assert 200 == resp.status_code, resp.get_data(as_text=True)
        password_email.assert_called_once()
        reset_token = password_email.call_args.args[2]
        assert reset_token

    updated_listener.reset_mock()
    resp = client.post(
        f"/reset_password/{reset_token}", data={"new_password": "newpassword123", "new_password2": "newpassword123"}
    )
    assert 302 == resp.status_code, resp.get_data(as_text=True)
    updated_listener.assert_called_once()

    resp = client.delete(
        f"/users/{user_id}",
    )
    assert resp.status_code == 200, resp.get_data(as_text=True)

    deleted_listener.assert_called_once()
    assert user_id == deleted_listener.call_args.kwargs["user"]["_id"]
    assert user["email"] == deleted_listener.call_args.kwargs["user"]["email"]
