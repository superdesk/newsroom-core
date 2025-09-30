from quart_babel import lazy_gettext
from newsroom.wire.embeds import remove_all_embeds

from .ninjs2 import NINJSFormatter2


class NINJSWithoutEmbedsFormatter(NINJSFormatter2):
    """
    Format with no Embeds, some API subscribers are unable to handle them!
    """

    format_id = "ninjs_exclude_embeds"
    name = lazy_gettext("Ninjs with no embeds")

    async def _transform_to_ninjs(self, item):
        remove_all_embeds(item)
        ninjs = await super()._transform_to_ninjs(item)
        return ninjs
