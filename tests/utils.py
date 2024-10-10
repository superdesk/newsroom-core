from typing import Dict, Any
from os import path
from quart.testing import QuartClient

from newsroom.users.service import UsersService
from superdesk.core import get_current_app, get_app_config, json
from superdesk.flask import url_for
from superdesk import get_resource_service
from superdesk.emails import SuperdeskMessage

from tests.fixtures import ADMIN_USER_EMAIL, PUBLIC_USER_EMAIL


async def post_json(client: QuartClient, url, data):
    """Post json data to client."""
    resp = await client.post(url, json=data)
    assert resp.status_code in [200, 201], "error %d on post to %s:\n%s" % (
        resp.status_code,
        url,
        await resp.get_data(),
    )
    return resp


async def patch_json(client: QuartClient, url, data):
    headers = await get_etag_header(client, url)
    resp = await client.patch(url, json=data, headers=headers)
    assert resp.status_code in (200, 201), "error {}: {} on patch to {}".format(
        resp.status_code,
        resp.data,
        url,
    )
    return resp.json


async def delete_json(client: QuartClient, url, data=None):
    headers = await get_etag_header(client, url)
    resp = await client.delete(url, json=data, headers=headers)
    assert resp.status_code in [200, 204], "error %d on delete to %s" % (
        resp.status_code,
        url,
    )
    return resp


async def get_etag_header(client: QuartClient, url):
    headers = {}
    orig = await (await client.get(url)).get_json()
    assert orig, "Could not fetch {}".format(url)
    if orig.get("_etag"):
        headers["IF-Match"] = orig["_etag"]
    return headers


async def get_json(client: QuartClient, url, expected_code=200):
    """Get json from client."""
    resp = await client.get(url, headers={"Accept": "application/json"})
    assert resp.status_code == expected_code, "error %d on get to %s:\n%s" % (
        resp.status_code,
        url,
        await resp.get_data(),
    )
    return json.loads(await resp.get_data())


def get_admin_user_id(app):
    from newsroom.tests.users import ADMIN_USER_ID

    return (get_resource_service("users").find_one(req=None, _id=ADMIN_USER_ID) or {}).get("_id")


def mock_send_email(to, subject, text_body, html_body=None, sender=None, sender_name=None, attachments_info=[]):
    if sender is None:
        sender = get_app_config("MAIL_DEFAULT_SENDER")

    msg = SuperdeskMessage(subject=subject, sender=sender, recipients=to)
    msg.body = text_body
    msg.html = html_body
    msg.attachments = [a["file_name"] for a in attachments_info]

    _app = get_current_app().as_any()._get_current_object()
    with _app.mail.connect() as connection:
        if connection:
            return connection.send(msg)

        return _app.mail.send(msg)


async def logout(client: QuartClient):
    await client.get(url_for("auth.logout"))


async def login(client: QuartClient, user, assert_login=True, follow_redirects=False, auto_logout=True):
    if auto_logout:
        await logout(client)

    resp = await client.post(
        url_for("auth.login"),
        form={
            "email": user["email"],
            "password": user.get("password") or "admin",
            # "remember_me": True,
        },
        follow_redirects=follow_redirects,
    )
    if assert_login:
        assert (
            resp.status_code == 302 if not follow_redirects else resp.status_code == 200
        ), f"Login failed for user {user['email']}"
    return resp


async def login_admin(client: QuartClient):
    return await login(client, {"email": ADMIN_USER_EMAIL})


async def login_public(client: QuartClient):
    return await login(client, {"email": PUBLIC_USER_EMAIL})


def load_fixture(filename: str) -> str:
    with open(path.join(path.dirname(__file__), "fixtures", filename), "r") as fixture:
        return fixture.read()


def load_json_fixture(filename: str) -> Dict[str, Any]:
    return json.loads(load_fixture(filename))


def add_fixture_to_db(resource: str, filename: str):
    item = load_json_fixture(filename)
    get_current_app().data.insert(resource, [item])
    return item


def get_resource_by_id(resource: str, item_id: str):
    return get_current_app().data.find_one(resource, req=None, _id=item_id)


async def get_user_by_email(email: str) -> Dict[str, Any]:
    new_user = await UsersService().find_by_email(email)
    assert new_user is not None
    return new_user.to_dict()
