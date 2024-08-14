import bson
import quart
import pathlib
import hashlib

from datetime import datetime
from quart_babel import lazy_gettext
from newsroom.template_filters import datetime_long, parse_date, format_event_datetime
from newsroom.template_loaders import template_locale
import newsroom.template_filters as template_filters


def test_parse_date():
    assert isinstance(parse_date("2017-11-03T13:49:48+0000"), datetime)
    assert isinstance(parse_date(datetime.now().isoformat()), datetime)


async def test_datetime_long_str(app):
    assert isinstance(datetime_long("2017-11-03T13:49:48+0000"), str)


async def test_theme_url():
    hash = hashlib.md5()
    file = pathlib.Path(__file__).parent.parent.parent.joinpath("newsroom/static/theme.css")
    with open(file, "rb") as f:
        hash.update(f.read())
    url = await quart.render_template_string("{{ theme_url('theme.css') }}")
    assert f"?h={hash.hexdigest()}" in url


async def test_to_json():
    object_id = bson.ObjectId()

    assert "foo" == await quart.render_template_string("{{ foo | tojson }}", foo="foo")
    assert '{"foo":"foo"}' == str(await quart.render_template_string("{{ obj | tojson }}", obj=dict(foo="foo")))

    assert "foo" == str(await quart.render_template_string("{{ foo | tojson }}", foo=lazy_gettext("foo")))
    assert '{"foo":"foo"}' == str(await quart.render_template_string("{{ obj | tojson }}", obj=dict(foo=lazy_gettext("foo"))))

    assert str(object_id) == str(await quart.render_template_string("{{ _id | tojson }}", _id=object_id))
    assert '{"_id":"%s"}' % (str(object_id),) == str(
        await quart.render_template_string("{{ obj | tojson }}", obj=dict(_id=object_id))
    )


async def test_notification_date_time_filters():
    with template_locale("fr_CA"):
        d = datetime(2023, 10, 31, 10, 0, 0)

        assert "11:00" == template_filters.notification_time(d)
        assert "octobre 31, 2023" == template_filters.notification_date(d)
        assert "11:00 octobre 31, 2023" == template_filters.notification_datetime(d)


async def test_format_event_datetime():
    # Case 1: Regular event with specific start and end times
    event1 = {
        "dates": {
            "tz": "Asia/Calcutta",
            "start": "2023-10-31T18:30:00+0000",
            "end": "2023-11-01T20:45:00+0000",
            "all_day": False,
            "no_end_time": False,
        },
    }
    assert "Date: 01/11/2023 00:00 to 02/11/2023 02:15 (Asia/Calcutta)" == await format_event_datetime(event1)

    # Case 2: All-day event
    event2 = {
        "dates": {
            "tz": "Asia/Calcutta",
            "end": "2023-12-18T18:29:59+0000",
            "start": "2023-12-17T18:30:00+0000",
            "all_day": True,
            "no_end_time": False,
        },
    }
    assert "Date: 18/12/2023 00:00 (Asia/Calcutta)" == await format_event_datetime(event2)

    # Case 3: Time-to-be-confirmed event
    event3 = {
        "dates": {
            "tz": "Asia/Calcutta",
            "start": "2023-10-31T18:30:00+0000",
            "end": "2023-11-01T20:45:00+0000",
            "all_day": False,
            "no_end_time": False,
        },
        "event": {
            "_time_to_be_confirmed": True,
        },
    }
    assert "Date: 01/11/2023 00:00 to 02/11/2023 02:15 (Asia/Calcutta) (Time to be confirmed)" == await format_event_datetime(
        event3
    )

    # Case 4: Event with no end time
    event4 = {
        "dates": {
            "tz": "Asia/Calcutta",
            "start": "2023-10-31T18:30:00+0000",
            "all_day": False,
            "no_end_time": True,
        }
    }
    assert "Date: 01/11/2023 00:00 (Asia/Calcutta)" == await format_event_datetime(event4)

    # Case 5: All-day event with no_end_time
    event5 = {
        "dates": {
            "tz": "Asia/Calcutta",
            "start": "2023-10-31T18:30:00+0000",
            "end": "2023-11-01T18:29:59+0000",
            "all_day": True,
            "no_end_time": True,
        },
    }
    assert "Date: 01/11/2023 00:00 (Asia/Calcutta)" == await format_event_datetime(event5)

    # Case 6: Multi-day event
    event6 = {
        "dates": {
            "tz": "Asia/Calcutta",
            "start": "2023-10-31T18:30:00+0000",
            "end": "2023-11-02T20:45:00+0000",
            "all_day": False,
            "no_end_time": False,
        },
    }
    assert "Date: 01/11/2023 00:00 to 03/11/2023 02:15 (Asia/Calcutta)" == await format_event_datetime(event6)

    # Case 7: REGULAR schedule_type with end_time
    event7 = {
        "dates": {
            "tz": "Asia/Calcutta",
            "start": "2023-11-01T19:29:59+0000",
            "end": "2023-11-02T15:30:00+0000",
            "all_day": False,
            "no_end_time": False,
        }
    }
    assert "Time: 00:59 AM to 21:00 PM on Date: November 2, 2023 (Asia/Calcutta)" == await format_event_datetime(event7)

    # Case 8: REGULAR schedule_type with no end time
    event8 = {
        "dates": {
            "tz": "Asia/Calcutta",
            "start": "2023-11-01T18:30:00+0000",
            "all_day": False,
            "no_end_time": True,
        },
    }
    assert "Date: 02/11/2023 00:00 (Asia/Calcutta)" == await format_event_datetime(event8)
