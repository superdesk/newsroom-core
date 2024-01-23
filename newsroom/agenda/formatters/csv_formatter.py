from newsroom.formatter import BaseFormatter
import csv
import io
import arrow
from werkzeug.utils import secure_filename
from newsroom.utils import parse_dates
from datetime import datetime
from typing import List, Dict, Any, Union, Tuple


class CSVFormatter(BaseFormatter):
    VERSION = "1.0"
    PRODID = "Newshub"
    FILE_EXTENSION = "csv"
    MIMETYPE = "text/csv"
    MULTI = True

    def format_item(self, item, item_type=None):
        event_item = self.format_event(item)
        return self.serialize_to_csv([event_item])

    def format_events(self, items: List[Dict[str, Any]], item_type: Union[str, None] = None) -> Tuple[bytes, str]:
        formatted_events = []
        for item in items:
            parse_dates(item)
            formatted_events.append(self.format_event(item))
        return self.serialize_to_csv(formatted_events), secure_filename(
            f"{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}-{'multi'}.{self.FILE_EXTENSION}"
        )

    def serialize_to_csv(self, items: List[Dict[str, Any]]) -> bytes:
        csv_string = io.StringIO()
        fieldnames: List[str] = list(items[0].keys())
        csv_writer: csv.DictWriter = csv.DictWriter(csv_string, delimiter=",", fieldnames=fieldnames)
        csv_writer.writeheader()
        for item in items:
            csv_writer.writerow(item)

        csv_string.seek(0)  # Reset the buffer position
        return csv_string.getvalue().encode("utf-8")

    def format_event(self, item: Dict[str, Any]) -> Dict[str, Any]:
        event = item.get("event", {})
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
            "Subject": self.format_list(event, "subject"),
            "Website": event.get("links")[0] if event.get("links") else "",
            "Category": self.format_list(event, "anpa_category"),
            "Event type": item.get("item_type", ""),
            "Organization name": event.get("event_contact_info")[0].get("organisation", " ")
            if event.get("event_contact_info")
            else "",
            "Contact": self.format_contact_info(item),
            "Coverage type": self.format_coverage(item, "coverage_type"),
            "Coverage status": self.format_coverage(item, "coverage_status"),
        }

    def datetime(self, value: Any) -> datetime:
        """Make sure dates are datetime instances."""
        return arrow.get(value).datetime

    def format_date(self, item: Dict[str, Any], date_type: str) -> str:
        date_obj = self.datetime(item.get("dates", {}).get(date_type))
        if date_obj:
            return date_obj.strftime("%Y-%m-%d")
        return ""

    def format_time(self, item: Dict[str, Any]) -> str:
        date_obj = item.get("dates", {})
        if date_obj.get("all_day"):
            return ""
        elif date_obj.get("no_end_time"):
            return f"{self.datetime(date_obj.get('start')).strftime('%H:%M:%S')}"
        else:
            return f"{self.datetime(date_obj.get('start')).strftime('%H:%M:%S')}-{self.datetime(date_obj.get('end')).strftime('%H:%M:%S')}"

    def format_location(self, item: Dict[str, Any], field: str) -> str:
        """
        format location info
        """
        if item.get("location"):
            for loc in item["location"]:
                return loc.get(field, "") if not field == "country" else loc.get("address", {}).get(field)
        return ""

    def format_list(self, item: Dict[str, Any], key: str) -> str:
        values = [v.get("name", "") for v in item.get(key, [])]
        return ",".join(values)

    def format_contact_info(self, item: Dict[str, Any]) -> str:
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
                return ",".join(contact_values)
        return ""

    def format_coverage(self, item: Dict[str, Any], field: str) -> str:
        """
        format coverage information
        """
        coverages = item.get("event", {}).get("coverages", {})
        value = []
        if coverages:
            for coverage in coverages:
                value.append(coverage.get(field, ""))
        return ",".join(value)
