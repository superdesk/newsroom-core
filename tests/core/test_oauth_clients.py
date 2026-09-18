from newsroom.oauth_clients.clients_async import ClientService
from newsroom.tests.users import test_login_succeeds_for_admin
from newsroom.auth_server.auth import JWTAuth
import base64


async def test_oauth_clients(client):
    await test_login_succeeds_for_admin(client)
    # Register a new client
    response = await client.post(
        "/oauth_clients/new",
        json={"name": "client11"},
    )
    assert response.status_code == 201

    # Check for the client secret
    response_json = await response.get_json()
    password = response_json.get("password", None)
    if not password:
        assert False

    # OAuth Token Generation using Basic Auth header
    username = response_json["_id"]
    userpass = username + ":" + password
    encoded_u = base64.b64encode(userpass.encode()).decode()

    payload = {"grant_type": "client_credentials"}
    token_auth_response = await client.post(
        "api/auth_server/token",
        headers={"Authorization": "Basic %s" % encoded_u},
        form=payload,
    )
    assert token_auth_response.status_code == 200

    token_auth_response_json = await token_auth_response.get_json()
    token = token_auth_response_json["access_token"]
    assert JWTAuth().check_auth(token=token, allowed_roles=None, resource=None, method=None)

    # OAuth Token Generation using client credentials in body.
    username = response_json["_id"]
    userpass = password

    payload = {
        "grant_type": "client_credentials",
        "client_id": username,
        "client_secret": userpass,
    }
    token_auth_response = await client.post(
        "api/auth_server/token",
        form=payload,
    )
    assert token_auth_response.status_code == 200

    token_auth_response_json = await token_auth_response.get_json()
    token = token_auth_response_json["access_token"]
    assert JWTAuth().check_auth(token=token, allowed_roles=None, resource=None, method=None)

    oauth_client = await ClientService().find_one(name="client11")

    # Update an existing client
    response = await client.post(
        "/oauth_clients/{}".format(str(oauth_client.id)),
        json={"name": "client2"},
    )

    assert response.status_code == 200

    # Delete an existing client
    response = await client.delete("/oauth_clients/{}".format(str(oauth_client.id)))
    assert response.status_code == 200
