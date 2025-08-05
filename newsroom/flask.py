from typing import Any, Optional
from quart import flash, send_from_directory, request


async def get_file_from_request(key: str) -> Optional[Any]:
    return (await request.files).get(key)


__all__ = ["flash", "send_from_directory", "get_file_from_request"]
