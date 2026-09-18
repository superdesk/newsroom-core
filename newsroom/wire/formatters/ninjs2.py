from quart_babel import lazy_gettext

from newsroom.wire.embeds import remove_internal_renditions
from .ninjs import NINJSFormatter
from newsroom.types import SectionEnum


class NINJSFormatter2(NINJSFormatter):
    """
    Overload the NINJSFormatter and add the associations as a field to copy
    """

    format_id = "ninjs2"
    name = lazy_gettext("Ninjs v2")
    # Sections set this is an API only format
    sections = [SectionEnum.NEWS_API]
    direct_copy_properties: set[str] = NINJSFormatter.direct_copy_properties.union(["associations"])

    async def _transform_to_ninjs(self, item):
        return remove_internal_renditions(await super()._transform_to_ninjs(item))
