from newsroom.formatter import BaseFormatter
import csv
import io


class CSVFormatter(BaseFormatter):
    VERSION = "1.0"
    PRODID = "Newshub"
    FILE_EXTENSION = "csv"
    MIMETYPE = "text/csv"

    def format_item(self, item, item_type=None):
        event_item = self.format_event(item)
        return self.serialize_to_csv(event_item)

    def serialize_to_csv(self, data):
        csv_string = io.StringIO()
        csv_writer = csv.DictWriter(csv_string, delimiter=",", fieldnames=data.keys())
        csv_writer.writeheader()
        csv_writer.writerow(data)  # Write a single row for the provided data
        csv_string.seek(0)  # Reset the buffer position
        return csv_string.getvalue().encode("utf-8")

    def format_event(self, item):
        event = item.get("event", {})
        return {
            "Event name": item.get("name", ""),
            "Description": item.get("definition_long", item.get("definition_short", "")),
            "Language": item.get("language", ""),
            "Event start date": self.format_date(item, "start"),
            "Event end date": self.format_date(item, "end"),
            "Event time": self.format_time(item),
            "Event timezone": item.get("dates", {}).get("tz", ""),
            "Location": self.parse_location(item, "name"),
            "Country": self.parse_location(item, "country"),
            "Subject": self.parse_list(event, "subject"),
            "Website": event.get("links")[0] if event.get("links") else "",
            "Category": self.parse_list(event, "anpa_category"),
            "Event type": item.get("item_type", ""),
            "Organization name": event.get("event_contact_info")[0].get("organisation", " ")
            if event.get("event_contact_info")
            else "",
            "Contact": self.parse_contact_info(item),
            "Coverage type": self.parse_coverage(item, "coverage_type"),
            "Coverage status": self.parse_coverage(item, "coverage_status"),
        }

    def format_date(self, item, date_type):
        date_obj = item.get("dates", {}).get(date_type)
        if date_obj:
            return date_obj.strftime("%Y-%m-%d")
        return ""

    def format_time(self, item):
        date_obj = item.get("dates", {})
        if date_obj.get("all_day"):
            return ""
        elif date_obj.get("no_end_time"):
            return f"{date_obj.get('start').strftime('%H:%M:%S')}"
        else:
            return f"{date_obj.get('start').strftime('%H:%M:%S')}-{date_obj.get('end').strftime('%H:%M:%S')}"

    def parse_location(self, item, field):
        """
        parse location info
        """
        if item.get("location"):
            for loc in item.get("location"):
                return loc.get(field, "") if not field == "country" else loc.get("address", {}).get(field)
        return ""

    def parse_list(self, item, key):
        values = [v.get("name", "") for v in item.get(key, [])]
        return ",".join(values)

    def parse_contact_info(self, item):
        """
        parse contact information
        """
        event_contact_info = item.get("event", {}).get("event_contact_info", [])

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

    def parse_coverage(self, item, field):
        """
        parse coverage information
        """
        coverages = item.get("event", {}).get("coverages", {})
        value = []
        if coverages:
            for coverage in coverages:
                value.append(coverage.get(field, ""))
        return ",".join(value)
