from quart_babel import lazy_gettext

from superdesk.flask import render_template

from newsroom.types import SectionEnum

from .base_wire_formatter import BaseWireFormatter
from .utils import log_media_downloads


class HTMLPackageFormatter(BaseWireFormatter):
    FILE_EXTENSION = "html"
    MIMETYPE = "application/zip"
    format_id = "html_package"
    name = lazy_gettext("HTML package")
    sections = [
        SectionEnum.WIRE,
        SectionEnum.FACTCHECK,
        SectionEnum.MONITORING,
        SectionEnum.MARKET_PLACE,
        SectionEnum.MEDIA_RELEASES,
    ]
    MULTI_ZIP = True

    async def format_item(self, item: dict, item_type: str | None = "items") -> bytes:
        await self.update_embeds(item)
        resp = str.encode(await render_template("download_embed.html", item=item), "utf-8")
        # log media as the last step in case something fails!
        await log_media_downloads(item)
        return resp
