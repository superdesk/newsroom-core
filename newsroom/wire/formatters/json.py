from typing import Any
from copy import deepcopy

from quart_babel import lazy_gettext

from superdesk.core import json
from planning.output_formatters.json_event import JsonEventFormatter
from planning.output_formatters.utils import expand_contact_info
from newsroom.template_filters import format_event_datetime
from newsroom.types import SectionEnum
from newsroom.formatters import BaseFormatter, FormatterAssetType
from newsroom.utils import url_for_agenda


agenda_json_fields = [
    "name",
    "slugline",
    "headline",
    "definition",
    "dates",
    "coverages",
    "service",
    "category",
    "place",
    "content_type",
    "related_events",
]


class JsonFormatter(BaseFormatter):
    format_id = "json"
    name = lazy_gettext("JSON")
    sections = [SectionEnum.AGENDA]
    assets = [FormatterAssetType.TEXT]

    MIMETYPE = "application/json"
    FILE_EXTENSION = "json"

    formatter = JsonEventFormatter()

    def format_coverages(self, item):
        fields = [
            "coverages",
            "delivery_id",
            "delivery_href",
            "deliveries",
            "coverage_id",
            "coverage_provider",
            "planning_id",
        ]
        for coverage in item.get("coverages") or []:
            for field in fields:
                coverage.pop(field, None)

    async def format_item(self, item: dict[str, Any], item_type: str | None = "items") -> bytes:
        from newsroom.agenda.utils import get_related_events

        if item_type == "wire":
            raise Exception("Undefined format for wire")

        output_item = deepcopy(item)
        output_item["event_contact_info"] = expand_contact_info(item.get("event_contact_info", []))

        self.format_coverages(output_item)

        if output_item.get("place"):
            output_item["place"] = [{"name": p.get("name")} for p in output_item.get("place", []) if p.get("name")]

        if output_item.get("subject"):
            output_item["category"] = [{"name": s.get("name")} for s in output_item.get("subject", []) if s.get("name")]

        if output_item.get("definition_long"):
            output_item["definition"] = output_item.get("definition_long")

        if output_item.get("genre"):
            output_item["content_type"] = output_item.get("genre")

        if output_item.get("event_ids"):
            related_events = await get_related_events(output_item)
            if related_events:
                filtered_related_events = []
                for event in related_events:
                    filtered_event = {
                        "url": url_for_agenda(event),
                        "name": event.get("name"),
                        "slugline": event.get("slugline"),
                        "headline": event.get("headline"),
                        "definition": event.get("definition_long"),
                        "dates": format_event_datetime(event),
                    }
                    filtered_related_events.append(filtered_event)

                output_item["related_events"] = filtered_related_events

        filtered_output_item = {k: output_item[k] for k in agenda_json_fields if k in output_item}

        return json.dumps(filtered_output_item, indent=2).encode()
