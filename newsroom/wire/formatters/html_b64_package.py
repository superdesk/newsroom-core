from lxml.html import HtmlElement
from quart_babel import lazy_gettext

from superdesk.flask import render_template
from superdesk.logging import logger

from newsroom.types import SectionEnum
from newsroom.assets.utils import get_media_file_as_base64
from newsroom.wire.formatters.base_wire_formatter import BaseWireFormatter
from newsroom.wire.formatters.utils import log_media_downloads


class HTMLMediaFormatter(BaseWireFormatter):
    """
    This formatter will render an HTML file with the media embedded as base64 encoded strings
    """

    FILE_EXTENSION = "html"
    MIMETYPE = "text/html"
    format_id = "html_media"
    name = lazy_gettext("HTML with embedded media")
    sections = [
        SectionEnum.WIRE,
        SectionEnum.FACTCHECK,
        SectionEnum.MONITORING,
        SectionEnum.MARKET_PLACE,
        SectionEnum.MEDIA_RELEASES,
    ]

    async def get_base64_file_data(self, embed_item: dict, use_widest_rendition: bool = False) -> str | None:
        if use_widest_rendition:
            rendition = self.get_widest_rendition(embed_item)
        else:
            rendition = embed_item.get("renditions", {}).get("original", {})

        if not rendition:
            return None

        src = rendition.get("media", "")
        mimetype = rendition.get("mimetype", "")

        file_data = await get_media_file_as_base64(src)
        if not file_data:
            logger.warning(f"Failed to retrieve media file for embed item: {embed_item}")
            return None

        return f"data:{mimetype};base64,{file_data.decode()}"

    async def update_image_element_attributes(self, embed_item: dict, elem: HtmlElement, embed_id: str) -> bool:
        elem.attrib["id"] = embed_id
        src = await self.get_base64_file_data(embed_item, use_widest_rendition=True)
        if src:
            elem.attrib["src"] = src
        return True

    async def update_av_element_attributes(self, embed_item: dict, elem: HtmlElement, embed_id: str) -> bool:
        elem.attrib["id"] = embed_id
        src = await self.get_base64_file_data(embed_item, use_widest_rendition=False)
        if src:
            elem.attrib["src"] = src
        elem.attrib.pop("alt", None)
        elem.attrib.pop("width", None)
        elem.attrib.pop("height", None)
        return True

    async def rewire_featuremedia(self, item: dict) -> None:
        """
        Set the references in the feature media to base64 encoded versions
        :param item:
        :return:
        """

        try:
            renditions = item["associations"]["featuremedia"]["renditions"]
        except (KeyError, TypeError):
            return

        for rendition in renditions.values():
            src: str = rendition.get("media", "")
            mimetype: str = rendition.get("mimetype", "")
            file_data = await get_media_file_as_base64(src)
            if file_data and mimetype:
                rendition["href"] = f"data:{mimetype};base64,{file_data.decode()}"

    async def format_item(self, item: dict, item_type: str | None = "items") -> bytes:
        await self.update_embeds(item)
        resp = str.encode(await render_template("download_embed.html", item=item), "utf-8")
        # log media as the last step in case something fails!
        await log_media_downloads(item)
        return resp
