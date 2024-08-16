from newsroom.settings import get_setting

from ..fixtures import items, init_items, init_auth, init_company  # noqa
from ..utils import post_json, get_json


async def test_general_settings(client, app):
    app.general_setting("foo", "Foo", default="bar")
    assert "bar" == get_setting("foo")
    await post_json(client, "/settings/general_settings", {"foo": "baz"})
    assert "baz" == get_setting("foo")
    await post_json(client, "/settings/general_settings", {"foo": ""})
    assert "bar" == get_setting("foo")

    # without key returns all settings with metadata
    assert "foo" in get_setting()
    assert "Foo" == get_setting()["foo"]["label"]
    assert "bar" == get_setting()["foo"]["default"]


async def test_boolean_settings(client, app):
    app.general_setting("foo", "Foo", default=False)
    assert get_setting("foo") is False
    await post_json(client, "/settings/general_settings", {"foo": True})
    assert get_setting("foo") is True
    await post_json(client, "/settings/general_settings", {"foo": False})
    assert get_setting("foo") is False
    await post_json(client, "/settings/general_settings", {"foo": None})
    assert get_setting("foo") is False

    app.general_setting("bar", "Bar", default=True)
    assert get_setting("bar") is True
    await post_json(client, "/settings/general_settings", {"bar": False})
    assert get_setting("bar") is False
    await post_json(client, "/settings/general_settings", {"bar": True})
    assert get_setting("bar") is True
    await post_json(client, "/settings/general_settings", {"foo": None})
    assert get_setting("bar") is True


async def test_news_only_filter(client, app):
    query = get_setting("news_only_filter")
    assert query is None

    # reset default filter
    app.config["NEWS_ONLY_FILTER"] = []

    _items = (await get_json(client, "/wire/search?newsOnly=1"))["_items"]
    assert len(_items) == 3

    await post_json(client, "/settings/general_settings", {"news_only_filter": "type:text"})

    _items = (await get_json(client, "/wire/search?newsOnly=1"))["_items"]
    assert len(_items) == 0
