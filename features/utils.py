import asyncio
from typing import Coroutine


def run_async(coro: Coroutine) -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(coro)
