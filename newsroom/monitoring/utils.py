from typing import Any
from io import BytesIO
from collections import OrderedDict
from datetime import date

from superdesk.errors import SuperdeskApiError
from superdesk.text_utils import get_text

from newsroom.types import MonitoringProfileResourceModel, WireItem
from newsroom.formatters import get_formatter
from newsroom.wire import WireItemService

from .formatters.base_monitoring_formatter import BaseMonitoringFormatter


def get_monitoring_formatter(format_id: str) -> BaseMonitoringFormatter:
    formatter = get_formatter(format_id)
    if not isinstance(formatter, BaseMonitoringFormatter):
        raise SuperdeskApiError.badRequestError("Formatter is not supported in Monitoring")
    return formatter


async def get_monitoring_file(
    monitoring_profile: MonitoringProfileResourceModel, items: list[WireItem] | list[dict[str, Any]]
) -> BytesIO:
    format_type = monitoring_profile.format_type or "monitoring_pdf"
    formatter = get_monitoring_formatter(format_type)
    return await formatter.get_monitoring_file(get_date_items_dict(items), monitoring_profile)


def get_keywords_in_text(text: str, keywords: list[str] | None) -> list[str]:
    """Get the list of keywords that are found in the provided text"""

    text_lower_case = text.lower()
    return [k for k in (keywords or []) if k.lower() in text_lower_case]


def get_date_items_dict(items: list[WireItem] | list[dict[str, Any]]) -> OrderedDict[date, list[dict[str, Any]]]:
    """Get an OrderedDict, grouped by date, from the provided WireItems"""

    date_items_dict: dict[date, list[dict[str, Any]]] = {}
    for item in items:
        wire_item = WireItem.from_dict(item) if isinstance(item, dict) else item
        item_date = wire_item.versioncreated.date()
        date_items_dict.setdefault(item_date, []).append(wire_item.to_dict())

    return OrderedDict(sorted(date_items_dict.items()))


def truncate_article_body(
    items: list[dict[str, Any]],
    monitoring_profile: MonitoringProfileResourceModel,
    full_text: bool = False,
) -> None:
    # To make sure PDF creator and RTF creator does truncate for linked_text settings
    # Manually truncate it
    for item in items:
        item["body_str"] = get_text(item.get("body_html", ""), content="html", lf_on_block=True)
        if monitoring_profile.alert_type == "linked_text":
            if not full_text and len(item["body_str"]) > 160:
                item["body_str"] = item["body_str"][:159] + "..."

        if monitoring_profile.format_type == "monitoring_pdf":
            body_lines = item.get("body_str", "").split("\n")
            altered_html = ""
            for line in body_lines:
                altered_html = '{}<div class="line">{}</div>'.format(altered_html, line)

            item["body_str"] = altered_html


async def get_items_for_monitoring_report(
    item_ids: list[str], monitoring_profile: MonitoringProfileResourceModel, full_text: bool = False
) -> list[dict[str, Any]]:
    """Get list of Wire items, and truncate the body_html based on MonitoringProfile attributes"""

    items = await WireItemService().find_by_ids_raw(item_ids)
    truncate_article_body(items, monitoring_profile, full_text)
    return items
