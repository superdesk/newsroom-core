from typing import Any

from quart_babel import lazy_gettext

from superdesk.flask import render_template

from newsroom.types import SectionEnum
from newsroom.formatters import BaseFormatter, FormatterAssetType


class TextFormatter(BaseFormatter):
    format_id = "text"
    name = lazy_gettext("Plain Text")
    sections = [SectionEnum.WIRE, SectionEnum.AGENDA]
    assets = [FormatterAssetType.TEXT]

    FILE_EXTENSION = "txt"
    MIMETYPE = "text/plain"

    async def format_item(self, item: dict[str, Any], item_type: str | None = "items") -> bytes:
        if item_type == "items":
            return str.encode(await render_template("download_item.txt", item=item), "utf-8")
        else:
            return str.encode(await render_template("download_agenda.txt", item=item), "utf-8")
