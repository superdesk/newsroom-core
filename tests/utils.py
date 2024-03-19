from typing import Dict, Any
from os import path
from flask import json, current_app as app, url_for
from flask.testing import FlaskClient

from superdesk import get_resource_service
from superdesk.emails import SuperdeskMessage


def post_json(client: FlaskClient, url, data):
    """Post json data to client."""
    resp = client.post(url, json=data)
    assert resp.status_code in [200, 201], "error %d on post to %s:\n%s" % (
        resp.status_code,
        url,
        resp.get_data().decode("utf-8"),
    )
    return resp


def patch_json(client: FlaskClient, url, data):
    headers = get_etag_header(client, url)
    resp = client.patch(url, json=data, headers=headers)
    assert resp.status_code in (200, 201), "error {}: {} on patch to {}".format(
        resp.status_code,
        resp.data,
        url,
    )
    return resp.json


def delete_json(client: FlaskClient, url, data=None):
    headers = get_etag_header(client, url)
    resp = client.delete(url, json=data, headers=headers)
    assert resp.status_code in [200, 204], "error %d on delete to %s" % (
        resp.status_code,
        url,
    )
    return resp


def get_etag_header(client: FlaskClient, url):
    headers = {}
    orig = client.get(url).json
    assert orig, "Could not fetch {}".format(url)
    if orig.get("_etag"):
        headers["IF-Match"] = orig["_etag"]
    return headers


def get_json(client: FlaskClient, url, expected_code=200):
    """Get json from client."""
    resp = client.get(url, headers={"Accept": "application/json"})
    assert resp.status_code == expected_code, "error %d on get to %s:\n%s" % (
        resp.status_code,
        url,
        resp.get_data().decode("utf-8"),
    )
    return json.loads(resp.get_data())


def get_admin_user_id(app):
    from newsroom.tests.users import ADMIN_USER_ID

    return (get_resource_service("users").find_one(req=None, _id=ADMIN_USER_ID) or {}).get("_id")


def mock_send_email(to, subject, text_body, html_body=None, sender=None, sender_name=None, attachments_info=[]):
    if sender is None:
        sender = app.config["MAIL_DEFAULT_SENDER"]

    msg = SuperdeskMessage(subject=subject, sender=sender, recipients=to)
    msg.body = text_body
    msg.html = html_body
    msg.attachments = [a["file_name"] for a in attachments_info]

    _app = app._get_current_object()
    with _app.mail.connect() as connection:
        if connection:
            return connection.send(msg)

        return _app.mail.send(msg)


def logout(client: FlaskClient):
    client.get(url_for("auth.logout"))


def login(client: FlaskClient, user, assert_login=True, follow_redirects=False, auto_logout=True):
    if auto_logout:
        logout(client)

    resp = client.post(
        url_for("auth.login"),
        data={
            "email": user["email"],
            "password": user.get("password") or "admin",
        },
        follow_redirects=follow_redirects,
    )
    if assert_login:
        assert (
            resp.status_code == 302 if not follow_redirects else resp.status_code == 200
        ), f"Login failed for user {user['email']}"
    return resp


def load_fixture(filename: str) -> str:
    with open(path.join(path.dirname(__file__), "fixtures", filename), "r") as fixture:
        return fixture.read()


def load_json_fixture(filename: str) -> Dict[str, Any]:
    return json.loads(load_fixture(filename))


def add_fixture_to_db(resource: str, filename: str):
    item = load_json_fixture(filename)
    _app = app._get_current_object()
    _app.data.insert(resource, [item])
    return item


def get_resource_by_id(resource: str, item_id: str):
    return app.data.find_one(resource, req=None, _id=item_id)
