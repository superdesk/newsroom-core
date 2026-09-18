from typing import Any

from quart_babel import lazy_gettext

from newsroom.types import SectionEnum

from .ninjs import NINJSFormatter
from .utils import log_media_downloads


class NINJSPackageFormatter(NINJSFormatter):
    """
    Overload the NINJSFormatter and add the associations as a field to copy
    """

    FILE_EXTENSION = "json"
    MIMETYPE = "application/zip"
    format_id = "ninjspackage"
    name = lazy_gettext("NINJS package")
    sections = [
        SectionEnum.WIRE,
        SectionEnum.FACTCHECK,
        SectionEnum.MONITORING,
        SectionEnum.MARKET_PLACE,
        SectionEnum.MEDIA_RELEASES,
    ]
    MULTI_ZIP = True
    direct_copy_properties: set[str] = NINJSFormatter.direct_copy_properties.union(["associations"])

    async def _transform_to_ninjs(self, item: dict[str, Any]):
        await self.update_embeds(item)
        resp = await super()._transform_to_ninjs(item)
        # log media as the last step in case something fails!
        await log_media_downloads(item)
        return resp
