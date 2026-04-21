from typing import Any
import asyncio
from quart import Quart

from flask_caching import Cache

from newsroom.core import get_current_wsgi_app


class NewshubCache(Cache):
    def __init__(self, app: Quart, *args, **kwargs):
        super().__init__(app, *args, **kwargs)  # type: ignore[arg-type]

    def init_app(self, app: Quart, config: dict | None = None) -> None:  # type: ignore[override]
        if app.config.get("CACHE_TYPE") == "redis":
            if config is None:
                config = {}

            config.setdefault("CACHE_OPTIONS", {})
            # Timeout for read/write operations (seconds)
            config["CACHE_OPTIONS"].setdefault("socket_timeout", app.config.get("CACHE_REDIS_TIMEOUT", 10))
            # Timeout for initial connection
            config["CACHE_OPTIONS"].setdefault(
                "socket_connect_timeout", app.config.get("CACHE_REDIS_CONNECT_TIMEOUT", 2)
            )
            # Optionally retry once after a timeout
            config["CACHE_OPTIONS"]["retry_on_timeout"] = True

        super().init_app(app, config)  # type: ignore[arg-type]

    def set_in_thread(self, key: str, value: Any, timeout: int | None = None):
        """
        Add/update a key/value pair in the cache, in a background thread.

        :param key: The key to set
        :param value: The value for the key
        :param timeout: The cache timeout for the key in seconds (if not
                        specified, it uses the default timeout). A timeout of
                        0 indicates that the cache never expires.
        """

        get_current_wsgi_app().add_background_task(self.set, key, value, timeout=timeout)

    def set_many_in_thread(self, mapping: dict, timeout: int | None = None) -> None:
        """
        Set multiple keys and values from a mapping, in a background thread.

        :param mapping: A mapping with the keys/values to set.
        :param timeout: The cache timeout for the key in seconds (if not
                        specified, it uses the default timeout). A timeout of
                        0 indicates that the cache never expires.
        """

        get_current_wsgi_app().add_background_task(self.set_many, mapping, timeout=timeout)

    def delete_in_thread(self, key: str) -> None:
        """
        Delete a key from the cache, in a background thread.

        :param key: The key to delete
        """

        get_current_wsgi_app().add_background_task(self.delete, key)

    def delete_many_in_thread(self, keys: list[str]):
        """
        Delete multiple keys from the cache, in a background thread.

        :param keys: The keys to delete
        """

        get_current_wsgi_app().add_background_task(self.delete_many, *keys)

    async def get_in_thread(self, key: str, async_timeout: int = 2) -> Any:
        """
        Look up key in the cache in a background thread, await until it's finished and return the result.

        :param key: The key to look up
        :param async_timeout: If the cache does not respond within this time, return None.
        :return: The value for the key, or None if the key is not found.
        """

        try:
            loop = asyncio.get_running_loop()
            return await asyncio.wait_for(loop.run_in_executor(None, self.get, key), timeout=async_timeout)
        except asyncio.TimeoutError:
            return None

    async def get_dict_in_thread(self, keys: list[str], async_timeout: int = 2) -> dict[str, Any] | None:
        """
        Return a dictionary of key/value pairs for the given keys.

        :param keys: The keys to look up
        :param async_timeout: If the cache does not respond within this time, return None.
        :return: A dictionary of key/value pairs, or None if the cache does not respond within the timeout.
        """

        try:
            loop = asyncio.get_running_loop()
            return await asyncio.wait_for(loop.run_in_executor(None, self.get_dict, *keys), timeout=async_timeout)
        except asyncio.TimeoutError:
            return None
