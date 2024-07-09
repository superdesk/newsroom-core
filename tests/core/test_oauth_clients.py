from flask import json
import pytest
from newsroom.tests.users import test_login_succeeds_for_admin
from superdesk import get_resource_service
from newsroom.auth_server.auth import JWTAuth
import base64


@pytest.mark.skip(reason="Pending to figure out some issue with OAuth2")
def test_oauth_clients(client):
    test_login_succeeds_for_admin(client)
    # Register a new client
    response = client.post(
        "/oauth_clients/new",
        data=json.dumps({"name": "client11"}),
        content_type="application/json",
    )
    assert response.status_code == 201

    # Check for the client secret
    password = response.json.get("password", None)
    if not password:
        assert False

    # OAuth Token Generation using Basic Auth header
    username = response.json["_id"]
    userpass = username + ":" + password
    encoded_u = base64.b64encode(userpass.encode()).decode()

    payload = {"grant_type": "client_credentials"}
    token_auth_response = client.post(
        "api/auth_server/token",
        headers={"Authorization": "Basic %s" % encoded_u},
        data=payload,
    )
    assert token_auth_response.status_code == 200

    token = token_auth_response.json["access_token"]
    assert JWTAuth.check_auth(self=None, token=token, allowed_roles=None, resource=None, method=None)

    oauth_client = get_resource_service("oauth_clients").find_one(req=None, name="client11")

    # OAuth Token Generation using client credentials in body.
    username = response.json["_id"]
    userpass = password

    payload = {
        "grant_type": "client_credentials",
        "client_id": username,
        "client_secret": userpass,
    }
    token_auth_response = client.post(
        "api/auth_server/token",
        data=payload,
    )
    assert token_auth_response.status_code == 200

    token = token_auth_response.json["access_token"]
    assert JWTAuth.check_auth(self=None, token=token, allowed_roles=None, resource=None, method=None)

    oauth_client = get_resource_service("oauth_clients").find_one(req=None, name="client11")

    # Update an existing client
    response = client.post(
        "/oauth_clients/{}".format(str(oauth_client["_id"])),
        data=json.dumps({"name": "client2"}),
        content_type="application/json",
    )

    assert response.status_code == 200

    # Delete an existing client
    response = client.delete("/oauth_clients/{}".format(str(oauth_client["_id"])))
    assert response.status_code == 200
