from unittest.mock import patch

from quart import Quart, Config

from newsroom.factory.cache import NewshubCache


def test_cache_redis_args() -> None:
    app = Quart(__name__)
    app.config = Config(".")
    app.config.from_object("newsroom.web.default_settings")

    with patch("flask_caching.backends.redis") as mock_redis_backend:
        NewshubCache(app)
        args, kwargs = mock_redis_backend.call_args
        assert args[3] == {
            "default_timeout": 3600,
            "retry_on_timeout": True,
            "socket_connect_timeout": 2.0,
            "socket_timeout": 10.0,
        }

    app.config.update({"CACHE_REDIS_TIMEOUT": 60, "CACHE_REDIS_CONNECT_TIMEOUT": 5})
    with patch("flask_caching.backends.redis") as mock_redis_backend:
        NewshubCache(app)
        args, kwargs = mock_redis_backend.call_args
        assert args[3] == {
            "default_timeout": 3600,
            "retry_on_timeout": True,
            "socket_connect_timeout": 5,
            "socket_timeout": 60,
        }


async def test_cache_get_set(app) -> None:
    # Use ``test_app`` here to make sure background task is finished before proceeding
    async with app.test_app():
        app.cache.set_in_thread("foo", "bar")

    foo = await app.cache.get_in_thread("foo")
    assert foo == "bar"


async def test_cache_many(app) -> None:
    number_of_docs = 100
    docs = {}
    for i in range(number_of_docs):
        docs[f"key{i}"] = f"value{i}"
    async with app.test_app():
        app.cache.set_many_in_thread(docs)

    results = await app.cache.get_dict_in_thread(docs.keys())
    for i in range(number_of_docs):
        assert results[f"key{i}"] == f"value{i}"
