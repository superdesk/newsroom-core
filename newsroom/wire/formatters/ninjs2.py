from quart_babel import lazy_gettext

from newsroom.news_api.utils import remove_internal_renditions, update_embed_urls, set_association_links
from .ninjs import NINJSFormatter
from .utils import remove_unpermissioned_embeds
from ...types import SectionEnum


class NINJSFormatter2(NINJSFormatter):
    """
    Overload the NINJSFormatter and add the associations as a field to copy
    """

    format_id = "ninjs2"
    name = lazy_gettext("Ninjs v2")
    # No sections this is an API only format
    sections = []

    def __init__(self):
        self.direct_copy_properties += ("associations",)

    async def _transform_to_ninjs(self, item):
        await remove_unpermissioned_embeds(item, section=SectionEnum.NEWS_API)
        update_embed_urls(item)
        set_association_links(item)
        return remove_internal_renditions(await super()._transform_to_ninjs(item))
