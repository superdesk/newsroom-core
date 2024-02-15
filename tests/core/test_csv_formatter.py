from .test_push_events import test_event
from flask import json
import copy
from newsroom.utils import get_entity_or_404
from newsroom.agenda.formatters import CSVFormatter
import csv


event = copy.deepcopy(test_event)
event["coverages"] = [
    {
        "planning_id": "urn:newsml:stt.fi:20280911:631023",
        "coverage_id": "ID_EVENT_286323",
        "scheduled": "2028-09-11T00:00:00+0000",
        "coverage_type": "text",
        "workflow_status": "draft",
        "coverage_status": "coverage intended",
        "slugline": "Testi/Luotsi",
    },
    {
        "planning_id": "urn:newsml:stt.fi:20280911:631025",
        "coverage_id": "ID_WORKREQUEST_187845",
        "scheduled": "2023-10-03T22:00:00+0000",
        "coverage_type": "picture",
        "workflow_status": "draft",
        "coverage_status": "coverage intended",
        "slugline": "Testi/Luotsi",
        "genre": [{"qcode": "sttimage:20", "name": "Kuvaaja paikalla"}],
    },
]
event["subject"] = [
    {"name": "Statistics & Economic Indicators", "qcode": "150", "scheme": "event_types", "code": "150"},
    {"name": "Economic Indicators", "qcode": "3", "scheme": "categories", "code": "3"},
    {
        "name": None,
        "qcode": "20001237",
        "parent": "08000000",
        "iptc_subject": None,
        "ap_subject": None,
        "in_jimi": False,
        "translations": {"name": {"en-CA": "anniversary", "fr-CA": None}},
        "scheme": "subject_custom",
        "code": "20001237",
    },
]
event["anpa_category"].append({"name": "Economic News", "qcode": "b", "code": "b"})

formatter = CSVFormatter()


def read_csv(data):
    csv_data = formatter.format_item(data, item_type="agenda")
    csv_string = csv_data.decode("utf-8")
    csv_lines = csv_string.split("\n")
    csv_reader = csv.reader(csv_lines)
    header = next(csv_reader)
    data_fields = next(csv_reader)
    return header, data_fields


def test_csv_formatter_item(client, app):
    client.post("/push", data=json.dumps(event), content_type="application/json")
    parsed = get_entity_or_404(event["guid"], "agenda")

    assert formatter.format_filename(parsed).endswith("new-press-conference.csv")

    header, data_fields = read_csv(parsed)

    expected_header_fields = [
        "Event name",
        "Description",
        "Language",
        "Event start date",
        "Event end date",
        "Event time",
        "Event timezone",
        "Location",
        "Country",
        "Subject",
        "Website",
        "Category",
        "Event type",
        "Organization name",
        "Contact",
        "Coverage type",
        "Coverage status",
    ]
    assert header == expected_header_fields

    expected_data_values = [
        "Prime minister press conference",
        "Ministers will check the environmental issues",
        "en-CA",
        "2018-05-28",
        "2018-05-28",
        "04:00:00-05:00:00",
        "Australia/Sydney",
        "Sydney",
        "Australia",
        "Statistics & Economic Indicators,Economic Indicators",
        "www.earthhour.com",
        "Australian General News,Economic News",
        "event",
        "AAP",
        "Professor,Tom,Jones,AAP,jones@foo.com",
        "text,picture",
        "coverage intended,coverage intended",
    ]
    assert data_fields == expected_data_values

    # CPCN-553

    event2 = {
        **event,
        "guid": "bar",
        "event_id": "bar",
        "slugline": "Latest Press conference",
        "subject": [
            {"name": "Statistics & Economic Indicators", "qcode": "150", "scheme": "event_types", "code": "150"},
            {"name": "Economic Indicators", "qcode": "3", "scheme": "categories", "code": "3"},
            {"name": "Asset allocation", "qcode": "subject:04000000", "scheme": "subject_custom"},
            {"name": "Basketball", "qcode": "3", "scheme": "categories", "code": "7"},
            {"name": "Market context", "qcode": "subject:03000000", "scheme": "subject_custom"},
        ],
        "event_contact_info": [
            {
                "_created": "2018-05-16T11:24:20+0000",
                "honorific": "",
                "_id": "5afc14e41d41c89668850f67",
                "first_name": "",
                "is_active": True,
                "organisation": "AAP",
                "contact_email": ["jones@foo.com"],
                "_updated": "2018-05-16T11:24:20+0000",
                "mobile": [],
                "contact_phone": [],
                "last_name": "",
                "public": True,
            }
        ],
    }
    client.post("/push", data=json.dumps(event2), content_type="application/json")
    parsed = get_entity_or_404(event2["guid"], "agenda")

    assert formatter.format_filename(parsed).endswith("latest-press-conference.csv")
    # update config
    app.config.update({"AGENDA_CSV_SUBJECT_SCHEMES": ["subject_custom"]})
    header2, data_fields2 = read_csv(parsed)
    assert header2 == expected_header_fields

    expected_data_values2 = [
        "Prime minister press conference",
        "Ministers will check the environmental issues",
        "en-CA",
        "2018-05-28",
        "2018-05-28",
        "04:00:00-05:00:00",
        "Australia/Sydney",
        "Sydney",
        "Australia",
        "Asset allocation,Market context",
        "www.earthhour.com",
        "Australian General News,Economic News",
        "event",
        "AAP",
        "AAP,jones@foo.com",
        "text,picture",
        "coverage intended,coverage intended",
    ]

    assert data_fields2 == expected_data_values2
