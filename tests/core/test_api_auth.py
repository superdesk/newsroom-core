from tests import utils


async def test_public_user_api(client, public_user):
    await utils.login(client, public_user)

    resp = await client.get("/api")
    assert 200 == resp.status_code

    resp = await client.get("/api/_users")
    assert resp.status_code == 401
