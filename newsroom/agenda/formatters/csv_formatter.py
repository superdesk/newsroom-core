
from newsroom.formatter import BaseFormatter
import csv
import io
from superdesk.utc import utcnow
# from typing import isinstance

class CSVFormatter(BaseFormatter):
    VERSION = "1.0"
    PRODID = "Newshub"
    FILE_EXTENSION = "csv"
    MIMETYPE = "text/csv"

    def format_item(self, item, item_type=None):

        
        event_item = self.format_event(item)
        csv_string = io.StringIO()
        csv_writer = csv.DictWriter(csv_string, delimiter=",", fieldnames=event_item.keys())
        csv_writer.writeheader()
        csv_writer.writerow(event_item)  # Write a single row for the provided item
        csv_string.seek(0)  # Reset the buffer position

        csv_data = csv_string.getvalue().encode('utf-8')  # Encode CSV data as bytes

        return csv_data
    

    def format_event(self, item):

        location , country = self.parse_location(item)

        return {
            "Event name": item.get("name", ""),
            "Description": item.get("definition_long", item.get("definition_short", "")),
            "Language": item.get("language", ""),
            "Event start date":item.get("dates", {}).get("start", "").strftime('%Y-%m-%d'),
            "Event end date": item.get("dates", {}).get("end", "").strftime('%Y-%m-%d'),
            "Event time":item.get("dates", {}).get("start", "").strftime('%H:%M:%S'),
            "Event timezone": item.get("dates", {}).get("tz", ""),
            "Location": location if location else "",
            "Country": country if country else "",
            "Subject": self.parse_subject(item),
            "Website": item.get("event", {}).get("links")[0],
            "Category": self.parse_category(item),
            "Event type": item.get("item_type", ""),
            "Organization name": item.get("event", {}).get("event_contact_info",{})[0].get("organisation"," "),
            "Contact": self.parse_contact_info(item),
            "Coverage type": self.parse_coverage(item, "coverage_type"),
            "Coverage status": self.parse_coverage(item, "coverage_status"),
        }
    

    def parse_location(self, item):
        """
        parse location
        """
        if item.get("location"):
            for loc in item.get("location"):
                return loc.get("name", ""), loc.get("country","")

        return ""
    
    def parse_subject(self, item):
        """
        parse subjects
        """
        event = item.get("event", {})
        subj = []
        if event.get("subject"):
            for subject in event.get("subject"):
                subj.append(subject.get("name", ""))
        return  ",".join(subj)


    def parse_category(self, item):
        event = item.get("event", {})
        cat = []
        if event.get("anpa_category"):
            for category in event.get("anpa_category"):
                cat.append(category.get("name", ""))
        return ",".join(cat)
    
    def parse_contact_info(self, item):
        event_contact_info = item.get("event", {}).get("event_contact_info", [])

        print(event_contact_info)
        contact_info_strings = []
        for contact in event_contact_info:
            contact_values = [
                contact.get("honorific", ""),
                contact.get("first_name", ""),
                contact.get("last_name", ""),
                contact.get("organisation", ""),
                ",".join(contact.get("contact_email", [])),
                ",".join(contact.get("mobile", []))
            ]
            print(contact_info_strings.append(",".join(contact_values)))
            return ",".join(contact_values)

    def parse_coverage(self, item, field):
        coverages = item.get("coverages", {})
        if coverages:
            for coverage in coverages:
                value = coverage.get(field,"")
            return ",".join(value)
        return ""

