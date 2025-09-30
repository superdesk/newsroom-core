from typing import Any
import json
from quart_babel import lazy_gettext

from superdesk.utils import json_serialize_datetime_objectId

from newsroom.types import SectionEnum

from .base_wire_formatter import BaseWireFormatter


class NINJSFormatter(BaseWireFormatter):
    format_id = "ninjs"
    name = lazy_gettext("Ninjs")
    sections = [SectionEnum.WIRE]

    MIMETYPE = "application/json"
    FILE_EXTENSION = "json"

    direct_copy_properties: set[str] = {
        "versioncreated",
        "usageterms",
        "language",
        "headline",
        "copyrightnotice",
        "urgency",
        "pubstatus",
        "mimetype",
        "copyrightholder",
        "ednote",
        "body_text",
        "body_html",
        "slugline",
        "keywords",
        "firstcreated",
        "firstpublished",
        "source",
        "extra",
        "annotations",
        "located",
        "byline",
        "description_html",
        "place",
        "embargoed",
        "priority",
        "genre",
        "service",
        "subject",
        "evolvedfrom",
        "original_id",
        "decsription_text",
    }

    async def format_item(self, item: dict[str, Any], item_type: str | None = "items") -> bytes:
        item = item.copy()
        ninjs = await self._transform_to_ninjs(item)

        return str.encode(json.dumps(ninjs, default=json_serialize_datetime_objectId), "utf-8")

    async def _transform_to_ninjs(self, item: dict[str, Any]) -> dict[str, Any]:
        ninjs = {
            "guid": item.get("_id"),
            "version": str(item.get("version", 1)),
            "type": "text",
        }

        for copy_property in self.direct_copy_properties:
            if item.get(copy_property) is not None:
                ninjs[copy_property] = item[copy_property]

        return ninjs
