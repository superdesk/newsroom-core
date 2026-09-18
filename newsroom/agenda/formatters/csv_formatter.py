from typing import Any
from datetime import datetime

import csv
import io
import arrow
from quart_babel import lazy_gettext
from werkzeug.utils import secure_filename

from superdesk.core import get_app_config

from newsroom.types import SectionEnum
from newsroom.formatters import BaseFormatter, FormatterAssetType
from newsroom.utils import parse_dates
from newsroom.agenda.utils import get_filtered_subject


class CSVFormatter(BaseFormatter):
    format_id = "Csv"
    name = lazy_gettext("CSV")
    sections = [SectionEnum.AGENDA]
    assets = [FormatterAssetType.TEXT]

    VERSION = "1.0"
    PRODID = "Newshub"
    FILE_EXTENSION = "csv"
    MIMETYPE = "text/csv"
    BULK_MIMETYPE = "text/csv"

    async def format_item(self, item: dict[str, Any], item_type: str | None = None) -> bytes:
        event_item = self.format_event(item)
        return self.serialize_to_csv([event_item])

    async def format_items(
        self, items: list[dict[str, Any]], item_type: str | None = None
    ) -> tuple[bytes | io.BytesIO, str | None]:
        formatted_events = []
        for item in items:
            parse_dates(item)
            formatted_events.append(self.format_event(item))
        return self.serialize_to_csv(formatted_events), secure_filename(
            f"{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}-multi.{self.FILE_EXTENSION}"
        )

    def serialize_to_csv(self, items: list[dict[str, Any]]) -> bytes:
        csv_string = io.StringIO()
        fieldnames: list[str] = list(items[0].keys())
        csv_writer: csv.DictWriter = csv.DictWriter(csv_string, delimiter=",", fieldnames=fieldnames)
        csv_writer.writeheader()
        for item in items:
            csv_writer.writerow(item)

        csv_string.seek(0)  # Reset the buffer position
        return csv_string.getvalue().encode("utf-8-sig")

    def format_event(self, item: dict[str, Any]) -> dict[str, Any]:
        subj_schemas = get_app_config("AGENDA_CSV_SUBJECT_SCHEMES", [])
        event = item.get("event", {})
        event["subject"] = get_filtered_subject(event.get("subject", []), subj_schemas)
        return {
            "Event name": item.get("name", ""),
            "Description": item.get("definition_long") or item.get("definition_short", "") or "",
            "Language": item.get("language", ""),
            "Event start date": self.format_date(item, "start"),
            "Event end date": self.format_date(item, "end"),
            "Event time": self.format_time(item),
            "Event timezone": item.get("dates", {}).get("tz", ""),
            "Location": self.format_location(item, "name"),
            "Country": self.format_location(item, "country"),
            "Subject": self.format_list(event, "subject", event.get("language")),
            "Website": event.get("links")[0] if event.get("links") else "",
            "Category": self.format_list(event, "anpa_category"),
            "Event type": item.get("item_type", ""),
            "Organization name": (
                event.get("event_contact_info")[0].get("organisation", " ") if event.get("event_contact_info") else ""
            ),
            "Contact": self.format_contact_info(item),
            "Coverage type": self.format_coverage(item, "coverage_type"),
            "Coverage status": self.format_coverage(item, "coverage_status"),
        }

    def datetime(self, value: Any) -> datetime:
        """Make sure dates are datetime instances."""
        return arrow.get(value).datetime

    def format_date(self, item: dict[str, Any], date_type: str) -> str:
        date_obj = self.datetime(item.get("dates", {}).get(date_type))
        if date_obj:
            return date_obj.strftime("%Y-%m-%d")
        return ""

    def format_time(self, item: dict[str, Any]) -> str:
        date_obj = item.get("dates", {})
        if date_obj.get("all_day"):
            return ""
        elif date_obj.get("no_end_time"):
            return f"{self.datetime(date_obj.get('start')).strftime('%H:%M:%S')}"
        else:
            return f"{self.datetime(date_obj.get('start')).strftime('%H:%M:%S')}-{self.datetime(date_obj.get('end')).strftime('%H:%M:%S')}"

    def format_location(self, item: dict[str, Any], field: str) -> str:
        """
        format location info
        """
        if item.get("location"):
            for loc in item["location"]:
                return loc.get(field, "") if not field == "country" else loc.get("address", {}).get(field)
        return ""

    def format_list(self, item: dict[str, Any], key: str, language: str | None = None) -> str:
        values = [get_translated_name(v, language) for v in item.get(key, [])]
        return ",".join(list(filter(bool, values)))

    def format_contact_info(self, item: dict[str, Any]) -> str:
        """
        format contact information
        """
        event_contact_info = item.get("event", {}).get("event_contact_info", [])
        if event_contact_info:
            for contact in event_contact_info:
                contact_values = [
                    contact.get("honorific", ""),
                    contact.get("first_name", ""),
                    contact.get("last_name", ""),
                    contact.get("organisation", ""),
                    ",".join(contact.get("contact_email", [])),
                    ",".join(contact.get("mobile", [])),
                ]
                return ",".join(list(filter(bool, contact_values)))
        return ""

    def format_coverage(self, item: dict[str, Any], field: str) -> str:
        """
        format coverage information
        """
        coverages = item.get("event", {}).get("coverages", {})
        value = []
        if coverages:
            for coverage in coverages:
                value.append(coverage.get(field, ""))
        return ",".join(value)


def get_translated_name(value: dict[str, Any], language: str | None = None) -> str:
    """
    Get translation for the given language
    """
    try:
        return value["translations"]["name"][language]
    except (KeyError, TypeError):
        return value.get("name", "")
