from typing import Any, Optional
from flask import flash, send_from_directory, request


def get_file_from_request(key: str) -> Optional[Any]:
    return request.files.get(key)


__all__ = ["flash", "send_from_directory", "get_file_from_request"]
