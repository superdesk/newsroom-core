from superdesk.flask import render_template
from .base import BaseFormatter


class TextFormatter(BaseFormatter):
    FILE_EXTENSION = "txt"
    MIMETYPE = "text/plain"

    async def format_item(self, item, item_type="items") -> bytes:
        if item_type == "items":
            return str.encode(await render_template("download_item.txt", item=item), "utf-8")
        else:
            return str.encode(await render_template("download_agenda.txt", item=item), "utf-8")
