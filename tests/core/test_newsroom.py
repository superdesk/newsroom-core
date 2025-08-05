import json
from tests.utils import logout


async def test_homepage_requires_auth(client, anonymous_user):
    await logout(client)
    response = await client.get("/")
    assert 302 == response.status_code
    assert b"login" in await response.get_data()


async def test_api_home(client, anonymous_user):
    await logout(client)
    response = await client.get("/api")
    assert 401 == response.status_code
    data = json.loads(await response.get_data())
    assert "_error" in data


async def test_news_search_fails_for_anonymous_user(client, anonymous_user):
    await logout(client)
    response = await client.get("/wire/search")
    assert 302 == response.status_code
    assert b"login" in await response.get_data()


async def test_agenda_search_fails_for_anonymous_user(client, anonymous_user):
    await logout(client)
    response = await client.get("/agenda/search")
    assert 302 == response.status_code
    assert b"login" in await response.get_data()
