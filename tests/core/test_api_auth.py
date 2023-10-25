from tests import utils


def test_public_user_api(client, public_user):
    utils.login(client, public_user)

    resp = client.get("/api")
    assert 200 == resp.status_code

    resp = client.get("/api/_users")
    assert resp.status_code == 401
