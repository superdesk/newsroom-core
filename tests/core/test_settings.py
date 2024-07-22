from newsroom.settings import get_setting

from ..fixtures import items, init_items, init_auth, init_company  # noqa
from ..utils import post_json, get_json


async def test_general_settings(client, app):
    app.general_setting("foo", "Foo", default="bar")
    assert "bar" == await get_setting("foo")
    post_json(client, "/settings/general_settings", {"foo": "baz"})
    assert "baz" == await get_setting("foo")
    post_json(client, "/settings/general_settings", {"foo": ""})
    assert "bar" == await get_setting("foo")

    # without key returns all settings with metadata
    assert "foo" in await get_setting()
    assert "Foo" == await get_setting()["foo"]["label"]
    assert "bar" == await get_setting()["foo"]["default"]


async def test_boolean_settings(client, app):
    app.general_setting("foo", "Foo", default=False)
    setting = await get_setting("foo")
    assert setting is False
    post_json(client, "/settings/general_settings", {"foo": True})
    assert setting is True
    post_json(client, "/settings/general_settings", {"foo": False})
    assert setting is False
    post_json(client, "/settings/general_settings", {"foo": None})
    assert setting is False

    app.general_setting("bar", "Bar", default=True)
    setting = await get_setting("bar")
    assert setting is True
    post_json(client, "/settings/general_settings", {"bar": False})
    assert setting is False
    post_json(client, "/settings/general_settings", {"bar": True})
    assert setting is True
    post_json(client, "/settings/general_settings", {"foo": None})
    assert setting is True


async def test_news_only_filter(client, app):
    query = await get_setting("news_only_filter")
    assert query is None

    # reset default filter
    app.config["NEWS_ONLY_FILTER"] = []

    _items = get_json(client, "/wire/search?newsOnly=1")["_items"]
    assert len(_items) == 3

    post_json(client, "/settings/general_settings", {"news_only_filter": "type:text"})

    _items = get_json(client, "/wire/search?newsOnly=1")["_items"]
    assert len(_items) == 0
