import os
import copy
from datetime import datetime

import icalendar
from quart import json

import newsroom.auth  # noqa - Fix cyclic import when running single test file
from newsroom.utils import get_entity_or_404
from newsroom.agenda.formatters import iCalFormatter
from .test_push_events import test_event

event = copy.deepcopy(test_event)
event["ednote"] = "ed note"
event["files"] = [
    {"media": "media-id", "name": "test.txt", "mimetype": "text/plain"},
]
event["dates"]["recurring_rule"] = {
    "frequency": "DAILY",
    "interval": 1,
    "count": 3,
}


async def test_ical_formatter_item(client, app, mocker):
    await client.post("/push", json=event)
    parsed = get_entity_or_404(event["guid"], "agenda")
    formatter = iCalFormatter()

    assert formatter.format_filename(parsed).endswith("new-press-conference.ical")

    mocker.patch(
        "newsroom.agenda.formatters.ical_formatter.utcnow",
        return_value=datetime(2018, 7, 30, 11, 9, 0),
    )
    ical = formatter.format_item(parsed, item_type="agenda")

    cal = icalendar.cal.Calendar.from_ical(ical)
    assert cal["version"] == "2.0"
    assert cal["prodid"] == "Newshub"
    assert 1 == len(cal.subcomponents)
    vevent = cal.subcomponents[0]
    assert vevent["uid"] == event["guid"]
    assert vevent["summary"] == event["name"]
    assert vevent["description"] == event["definition_long"]
    assert vevent["dtstart"].to_ical() == b"20180528T040000Z"
    assert vevent["dtend"].to_ical() == b"20180528T050000Z"
    assert vevent["dtstamp"].to_ical() == b"20180730T110900Z"
    assert vevent["attach"] == "http://localhost:5050/assets/media-id"
    assert vevent["geo"].to_ical() == "-33.8548157;151.2164539"
    assert vevent["location"] == "Sydney"
    assert vevent["categories"].to_ical() == b"Sport"
    assert vevent["comment"] == event["ednote"]
    assert vevent["url"] == event["links"][0]
    assert vevent["contact"] == "Professor Tom Jones, AAP, jones@foo.com"
    assert vevent["rrule"].to_ical() == b"FREQ=DAILY;COUNT=3;INTERVAL=1"


async def test_ical_formatter_failing(client, app):
    with open(
        os.path.join(os.path.dirname(__file__), "../fixtures", "agenda_fixture.json"),
        "r",
    ) as fixture:
        item = json.load(fixture)
    formatter = iCalFormatter()
    formatter.format_item(item, item_type="agenda")


def test_onclusive_all_day():
    event = {
        "name": "test",
        "dates": {
            "start": "2024-01-01T00:00:00",
            "end": "2024-01-03T00:00:00",
            "all_day": True,
        },
    }
    formatter = iCalFormatter()
    output = formatter.format_item(event, item_type="agenda").decode("utf-8")
    assert "DTSTART;VALUE=DATE:20240101" in output
    assert "DTEND;VALUE=DATE:20240103" in output


def test_onclusive_no_end_time():
    event = {
        "name": "test",
        "dates": {
            "start": "2024-01-01T10:00:00",
            "end": "2024-01-03T00:00:00",
            "no_end_time": True,
        },
    }
    formatter = iCalFormatter()
    output = formatter.format_item(event, item_type="agenda").decode("utf-8")
    assert "DTSTART:20240101T100000Z" in output
    assert "DTEND;VALUE=DATE:20240103" in output
