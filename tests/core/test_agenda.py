import pytz
from flask import json
from datetime import datetime, timedelta
from urllib import parse
from unittest import mock
from pytest import fixture

import newsroom.auth  # noqa - Fix cyclic import when running single test file
from newsroom.utils import (
    get_location_string,
    get_agenda_dates,
    get_public_contacts,
    get_entity_or_404,
    get_local_date,
    get_end_date,
)
from tests.utils import (
    post_json,
    delete_json,
    get_json,
    get_admin_user_id,
    mock_send_email,
)
from tests.fixtures import PUBLIC_USER_ID, COMPANY_1_ID
from .utils import add_company_products

from copy import deepcopy
from bson import ObjectId
from newsroom.agenda.agenda import get_date_filters

date_time_format = "%Y-%m-%dT%H:%M:%S"

test_planning = {
    "description_text": "description here",
    "abstract": "abstract text",
    "_current_version": 1,
    "agendas": [],
    "anpa_category": [{"name": "Entertainment", "subject": "01000000", "qcode": "e"}],
    "item_id": "foo",
    "ednote": "ed note here",
    "slugline": "Vivid planning item",
    "headline": "Planning headline",
    "planning_date": "2018-05-28T10:51:52+0000",
    "state": "scheduled",
    "item_class": "plinat:newscoverage",
    "coverages": [
        {
            "planning": {
                "g2_content_type": "text",
                "slugline": "Vivid planning item",
                "internal_note": "internal note here",
                "genre": [{"name": "Article (news)", "qcode": "Article"}],
                "ednote": "ed note here",
                "scheduled": "2018-05-28T10:51:52+0000",
            },
            "news_coverage_status": {
                "name": "coverage intended",
                "label": "Planned",
                "qcode": "ncostat:int",
            },
            "workflow_status": "draft",
            "firstcreated": "2018-05-28T10:55:00+0000",
            "coverage_id": "213",
        }
    ],
    "_id": "foo",
    "urgency": 3,
    "guid": "foo",
    "name": "This is the name of the vivid planning item",
    "subject": [{"name": "library and museum", "qcode": "01009000", "parent": "01000000"}],
    "pubstatus": "usable",
    "type": "planning",
}


@fixture
def agenda_user(client, app):
    add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "name": "product test",
                "query": "headline:test",
                "is_enabled": True,
                "product_type": "agenda",
            },
            {
                "name": "product test 2",
                "query": "slugline:prime",
                "is_enabled": True,
                "product_type": "agenda",
            },
        ],
    )

    with client.session_transaction() as session:
        session["user"] = PUBLIC_USER_ID
        session["user_type"] = "public"

    return PUBLIC_USER_ID


def mock_utcnow():
    return datetime.strptime("2018-11-23T22:00:00", date_time_format)


def test_item_detail(client):
    resp = client.get("/agenda/urn:conference")
    assert resp.status_code == 200
    assert "urn:conference" in resp.get_data().decode()
    assert "Conference Planning" in resp.get_data().decode()


def test_item_json(client):
    resp = client.get("/agenda/urn:conference?format=json")
    data = json.loads(resp.get_data())
    assert "headline" in data
    assert "files" in data["event"]
    assert "internal_note" in data["event"]
    assert "internal_note" in data["planning_items"][0]
    assert "internal_note" in data["coverages"][0]["planning"]


def test_item_json_does_not_return_files(client, app):
    # public user
    with client.session_transaction() as session:
        session["user"] = PUBLIC_USER_ID
        session["user_type"] = "public"

    data = get_json(client, "/agenda/urn:conference?format=json")
    assert "headline" in data
    assert "files" not in data["event"]
    assert "internal_note" not in data["event"]
    assert "internal_note" not in data["planning_items"][0]
    assert "internal_note" not in data["coverages"][0]["planning"]


def get_bookmarks_count(client, user):
    resp = client.get("/agenda/search?bookmarks=%s" % str(user))
    assert resp.status_code == 200
    data = json.loads(resp.get_data())
    return data["_meta"]["total"]


def test_basic_search(client, agenda_user):
    resp = client.get("/agenda/search?q=headline")
    assert resp.status_code == 200
    data = json.loads(resp.get_data())
    assert data["_meta"]["total"]


def test_search_with_accents(client, agenda_user):
    resp = client.get("/agenda/search?q=héadlíne")
    assert resp.status_code == 200
    data = json.loads(resp.get_data())
    assert data["_meta"]["total"]


def test_bookmarks(client, app):
    user_id = get_admin_user_id(app)
    assert user_id

    assert 0 == get_bookmarks_count(client, user_id)

    resp = client.post(
        "/agenda_bookmark",
        data=json.dumps(
            {
                "items": ["urn:conference"],
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 200

    assert 1 == get_bookmarks_count(client, user_id)

    client.delete(
        "/agenda_bookmark",
        data=json.dumps(
            {
                "items": ["urn:conference"],
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 200

    assert 0 == get_bookmarks_count(client, user_id)


def test_item_copy(client, app):
    resp = client.post(
        "/wire/{}/copy?type=agenda".format("urn:conference"),
        content_type="application/json",
    )
    assert resp.status_code == 200

    resp = client.get("/agenda/urn:conference?format=json")
    data = json.loads(resp.get_data())
    assert "copies" in data

    user_id = get_admin_user_id(app)
    assert str(user_id) in data["copies"]


@mock.patch("newsroom.email.send_email", mock_send_email)
def test_share_items(client, app, mocker):
    user_ids = app.data.insert(
        "users",
        [
            {
                "email": "foo2@bar.com",
                "first_name": "Foo",
                "last_name": "Bar",
                "receive_email": True,
            }
        ],
    )

    with app.mail.record_messages() as outbox:
        resp = client.post(
            "/wire_share?type=agenda",
            data=json.dumps(
                {
                    "items": ["urn:conference"],
                    "users": [str(user_ids[0])],
                    "message": "Some info message",
                }
            ),
            content_type="application/json",
        )

        assert resp.status_code == 201, resp.get_data().decode("utf-8")
        assert len(outbox) == 1
        assert outbox[0].recipients == ["foo2@bar.com"]
        assert outbox[0].subject == "From Newshub: test headline"
        assert "Hi Foo Bar" in outbox[0].body
        assert "admin admin (admin@sourcefabric.org) shared " in outbox[0].body
        assert "Conference Planning" in outbox[0].body
        assert "http://localhost:5050/agenda?item=urn%3Aconference" in outbox[0].body
        assert "Some info message" in outbox[0].body

    resp = client.get("/agenda/{}?format=json".format("urn:conference"))
    data = json.loads(resp.get_data())
    assert "shares" in data

    user_id = get_admin_user_id(app)
    assert str(user_id) in data["shares"]


def test_agenda_search_filtered_by_query_product(client, app, public_company):
    NAV_1 = ObjectId("5e65964bf5db68883df561c0")
    NAV_2 = ObjectId("5e65964bf5db68883df561c1")

    app.data.insert(
        "navigations",
        [
            {
                "_id": NAV_1,
                "name": "navigation-1",
                "is_enabled": True,
                "product_type": "agenda",
            },
            {
                "_id": NAV_2,
                "name": "navigation-2",
                "is_enabled": True,
                "product_type": "agenda",
            },
        ],
    )

    add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "name": "product test",
                "query": "headline:test",
                "navigations": [NAV_1],
                "is_enabled": True,
                "product_type": "agenda",
            },
            {
                "name": "product test 2",
                "query": "slugline:prime",
                "navigations": [NAV_2],
                "is_enabled": True,
                "product_type": "agenda",
            },
        ],
    )

    with client.session_transaction() as session:
        session["user"] = "59b4c5c61d41c8d736852fbf"
        session["user_type"] = "public"

    resp = client.get("/agenda/search")
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])
    assert "_aggregations" in data
    assert "files" not in data["_items"][0]["event"]
    assert "internal_note" not in data["_items"][0]["event"]
    assert "internal_note" not in data["_items"][0]["planning_items"][0]
    assert "internal_note" not in data["_items"][0]["planning_items"][0]["coverages"][0]["planning"]
    assert "internal_note" not in data["_items"][0]["coverages"][0]["planning"]
    resp = client.get(f"/agenda/search?navigation={NAV_1}")
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])
    assert "_aggregations" in data


@mock.patch("newsroom.email.send_email", mock_send_email)
def test_coverage_request(client, app):
    post_json(
        client,
        "/settings/general_settings",
        {"coverage_request_recipients": "admin@bar.com"},
    )
    with app.mail.record_messages() as outbox:
        resp = client.post(
            "/agenda/request_coverage",
            data=json.dumps(
                {
                    "item": "urn:conference",
                    "message": "Some info message",
                }
            ),
            content_type="application/json",
        )

        assert resp.status_code == 201, resp.get_data().decode("utf-8")
        assert len(outbox) == 1
        assert outbox[0].recipients == ["admin@bar.com"]
        assert outbox[0].subject == "Coverage inquiry: Conference Planning"
        assert "admin admin" in outbox[0].body
        assert "admin@sourcefabric.org" in outbox[0].body
        assert "http://localhost:5050/agenda?item={}".format(parse.quote("urn:conference")) in outbox[0].body
        assert "Some info message" in outbox[0].body


def test_watch_event(client, app):
    user_id = get_admin_user_id(app)
    assert 0 == get_bookmarks_count(client, user_id)

    post_json(client, "/agenda_watch", {"items": ["urn:conference"]})
    assert 1 == get_bookmarks_count(client, user_id)

    delete_json(client, "/agenda_watch", {"items": ["urn:conference"]})
    assert 0 == get_bookmarks_count(client, user_id)


def test_watch_coverages(client, app):
    user_id = get_admin_user_id(app)

    post_json(
        client,
        "/agenda_coverage_watch",
        {
            "coverage_id": "urn:coverage",
            "item_id": "urn:conference",
        },
    )

    after_watch_item = get_entity_or_404("urn:conference", "agenda")
    assert after_watch_item["coverages"][0]["watches"] == [user_id]


def test_unwatch_coverages(client, app):
    user_id = get_admin_user_id(app)

    post_json(
        client,
        "/agenda_coverage_watch",
        {
            "coverage_id": "urn:coverage",
            "item_id": "urn:conference",
        },
    )

    after_watch_item = get_entity_or_404("urn:conference", "agenda")
    assert after_watch_item["coverages"][0]["watches"] == [user_id]

    delete_json(
        client,
        "/agenda_coverage_watch",
        {
            "coverage_id": "urn:coverage",
            "item_id": "urn:conference",
        },
    )

    after_watch_item = get_entity_or_404("urn:conference", "agenda")
    assert after_watch_item["coverages"][0]["watches"] == []


def test_remove_watch_coverages_on_watch_item(client, app):
    user_id = ObjectId(get_admin_user_id(app))
    other_user_id = PUBLIC_USER_ID

    test_planning_coverage_watches = deepcopy(test_planning)
    test_planning_coverage_watches["coverages"][0]["watches"] = [other_user_id]
    client.post(
        "/push",
        data=json.dumps(test_planning_coverage_watches),
        content_type="application/json",
    )

    post_json(
        client,
        "/agenda_coverage_watch",
        {
            "coverage_id": test_planning_coverage_watches["coverages"][0]["coverage_id"],
            "item_id": test_planning_coverage_watches["_id"],
        },
    )

    after_watch_coverage_item = get_entity_or_404(test_planning_coverage_watches["_id"], "agenda")
    assert str(other_user_id) in after_watch_coverage_item["coverages"][0]["watches"]
    assert user_id in after_watch_coverage_item["coverages"][0]["watches"]

    post_json(client, "/agenda_watch", {"items": [test_planning_coverage_watches["_id"]]})
    after_watch_item = get_entity_or_404(test_planning_coverage_watches["_id"], "agenda")
    assert after_watch_item["coverages"][0]["watches"] == [str(other_user_id)]
    assert after_watch_item["watches"] == [user_id]


def test_fail_watch_coverages(client, app):
    user_id = get_admin_user_id(app)

    post_json(client, "/agenda_watch", {"items": ["urn:conference"]})
    after_watch_item = get_entity_or_404("urn:conference", "agenda")
    assert after_watch_item["watches"] == [user_id]

    with client.session_transaction() as session:
        session["user"] = str(PUBLIC_USER_ID)
        session["user_type"] = "public"
        request = {
            "coverage_id": "urn:coverage",
            "item_id": "urn:conference",
        }

        # Add a coverage watch
        resp = client.post(
            "/agenda_coverage_watch",
            data=json.dumps(request, indent=2),
            content_type="application/json",
        )
        assert resp.status_code == 403

        # Remove a coverage watch
        resp = client.delete(
            "/agenda_coverage_watch",
            data=json.dumps(request, indent=2),
            content_type="application/json",
        )
        assert resp.status_code == 403


@mock.patch("newsroom.utils.get_utcnow", mock_utcnow)
def test_local_time(client, app, mocker):
    # 9 am Sydney Time - day light saving on
    local_date = get_local_date("now/d", "00:00:00", -660)
    assert "2018-11-23T13:00:00" == local_date.strftime(date_time_format)

    local_date = get_local_date("now/w", "00:00:00", -660)
    assert "2018-11-18T13:00:00" == local_date.strftime(date_time_format)

    local_date = get_local_date("now/M", "00:00:00", -660)
    assert "2018-10-31T13:00:00" == local_date.strftime(date_time_format)

    local_date = get_local_date("2018-11-24", "00:00:00", -660)
    assert "2018-11-23T13:00:00" == local_date.strftime(date_time_format)

    end_local_date = get_local_date("2018-11-24", "23:59:59", -660)
    assert "2018-11-24T12:59:59" == end_local_date.strftime(date_time_format)

    end_date = get_end_date("now/d", end_local_date)
    assert "2018-11-24T12:59:59" == end_date.strftime(date_time_format)

    end_date = get_end_date("now/w", end_local_date)
    assert "2018-11-30T12:59:59" == end_date.strftime(date_time_format)

    end_date = get_end_date("now/M", end_local_date)
    assert "2018-12-23T12:59:59" == end_date.strftime(date_time_format)


def test_get_location_string():
    agenda = {}
    assert get_location_string(agenda) == ""

    agenda["location"] = []
    assert get_location_string(agenda) == ""

    agenda["location"] = [{"name": "test location", "address": {"locality": "inner city"}}]
    assert get_location_string(agenda) == "test location, inner city"

    agenda["location"] = [
        {
            "name": "Sydney Opera House",
            "address": {
                "country": "Australia",
                "type": "arts_centre",
                "postal_code": "2000",
                "title": "Opera v Sydney",
                "line": ["2 Macquarie Street"],
                "locality": "Sydney",
                "area": "Sydney",
            },
        }
    ]
    assert get_location_string(agenda) == "Sydney Opera House, 2 Macquarie Street, Sydney, Sydney, 2000, Australia"


def test_get_public_contacts():
    agenda = {}
    assert get_public_contacts(agenda) == []

    agenda["event"] = {}
    assert get_public_contacts(agenda) == []

    agenda["event"]["event_contact_info"] = [
        {
            "_created": "2018-05-16T11:24:20+0000",
            "honorific": "Professor",
            "_id": "5afc14e41d41c89668850f67",
            "first_name": "Tom",
            "is_active": True,
            "organisation": "AAP",
            "contact_email": ["jones@foo.com"],
            "_updated": "2018-05-16T11:24:20+0000",
            "mobile": [],
            "contact_phone": [],
            "last_name": "Jones",
            "public": True,
        }
    ]
    assert get_public_contacts(agenda) == [
        {
            "name": "Tom Jones",
            "organisation": "AAP",
            "phone": "",
            "email": "jones@foo.com",
            "mobile": "",
        }
    ]


def test_get_agenda_dates():
    agenda = {
        "dates": {
            "end": datetime.strptime("2018-05-28T06:00:00+0000", "%Y-%m-%dT%H:%M:%S+0000").replace(tzinfo=pytz.UTC),
            "start": datetime.strptime("2018-05-28T05:00:00+0000", "%Y-%m-%dT%H:%M:%S+0000").replace(tzinfo=pytz.UTC),
        },
    }
    assert get_agenda_dates(agenda) == "07:00 - 08:00, 28/05/2018"

    agenda = {
        "dates": {
            "end": datetime.strptime("2018-05-30T06:00:00+0000", "%Y-%m-%dT%H:%M:%S+0000").replace(tzinfo=pytz.UTC),
            "start": datetime.strptime("2018-05-28T05:00:00+0000", "%Y-%m-%dT%H:%M:%S+0000").replace(tzinfo=pytz.UTC),
        },
    }
    assert get_agenda_dates(agenda) == "07:00 28/05/2018 - 08:00 30/05/2018"

    agenda = {
        "dates": {
            "end": datetime.strptime("2018-05-28T21:59:00+0000", "%Y-%m-%dT%H:%M:%S+0000").replace(tzinfo=pytz.UTC),
            "start": datetime.strptime("2018-05-27T22:00:00+0000", "%Y-%m-%dT%H:%M:%S+0000").replace(tzinfo=pytz.UTC),
        },
    }
    assert get_agenda_dates(agenda) == "ALL DAY 28/05/2018"

    agenda = {
        "dates": {
            "end": datetime.strptime("2018-05-30T06:00:00+0000", "%Y-%m-%dT%H:%M:%S+0000").replace(tzinfo=pytz.UTC),
            "start": datetime.strptime("2018-05-30T06:00:00+0000", "%Y-%m-%dT%H:%M:%S+0000").replace(tzinfo=pytz.UTC),
        },
    }
    assert get_agenda_dates(agenda) == "08:00 30/05/2018"

    agenda = {
        "dates": {
            "end": datetime.strptime("2018-05-30T00:00:00+0000", "%Y-%m-%dT%H:%M:%S+0000").replace(tzinfo=pytz.UTC),
            "start": datetime.strptime("2018-05-30T00:00:00+0000", "%Y-%m-%dT%H:%M:%S+0000").replace(tzinfo=pytz.UTC),
            "all_day": True,
        },
    }
    assert get_agenda_dates(agenda) == "May 30, 2018"

    agenda = {
        "dates": {
            "end": datetime.strptime("2018-05-30T08:00:00+0000", "%Y-%m-%dT%H:%M:%S+0000").replace(tzinfo=pytz.UTC),
            "start": datetime.strptime("2018-05-30T06:00:00+0000", "%Y-%m-%dT%H:%M:%S+0000").replace(tzinfo=pytz.UTC),
            "all_day": True,
        },
    }
    assert get_agenda_dates(agenda) == "May 30, 2018"

    agenda = {
        "dates": {
            "end": datetime.strptime("2018-05-30T00:00:00+0000", "%Y-%m-%dT%H:%M:%S+0000").replace(tzinfo=pytz.UTC),
            "start": datetime.strptime("2018-05-27T04:00:00+0000", "%Y-%m-%dT%H:%M:%S+0000").replace(tzinfo=pytz.UTC),
            "all_day": True,
        },
    }
    assert get_agenda_dates(agenda) == "May 27, 2018 - May 30, 2018"


def test_filter_agenda_by_coverage_status(client):
    client.post("/push", data=json.dumps(test_planning), content_type="application/json")

    test_planning["guid"] = "bar"
    test_planning["coverages"][0]["news_coverage_status"] = {
        "name": "coverage not intended",
        "label": "Not Planned",
        "qcode": "ncostat:fint",
    }
    client.post("/push", data=json.dumps(test_planning), content_type="application/json")

    test_planning["guid"] = "baz"
    test_planning["planning_date"] = ("2018-05-28T10:45:52+0000",)
    test_planning["coverages"] = []
    client.post("/push", data=json.dumps(test_planning), content_type="application/json")

    test_planning["guid"] = "123foo"
    test_planning["planning_date"] = "2023-08-17T10:45:52+0000"
    test_planning["coverages"] = (
        {
            "coverage_id": "placeholder_urn:newsml:stt.fi:20230529:620121",
            "workflow_status": "draft",
            "firstcreated": "2023-08-17T10:45:52+0000",
            "planning": {
                "slugline": "Placeholder Coverage",
                "g2_content_type": "text",
                "scheduled": "2023-08-17T10:45:52+0000",
            },
            "flags": {"placeholder": True},
            "news_coverage_status": {
                "name": "coverage not decided yet",
                "label": "On merit",
                "qcode": "ncostat:notdec",
            },
        },
        {
            "planning": {
                "g2_content_type": "audio",
                "slugline": "Vivid planning item",
                "scheduled": "2018-05-28T10:51:52+0000",
            },
            "news_coverage_status": {
                "name": "coverage intended",
                "label": "Planned",
                "qcode": "ncostat:int",
            },
            "workflow_status": "completed",
            "firstcreated": "2018-05-28T10:55:00+0000",
            "coverage_id": "placeholder_urn:newsml:stt.fi:20230529:620123",
            "deliveries": [
                {
                    "publish_time": "2018-05-30T10:55:00+0000",
                    "delivery_state": "published",
                }
            ],
        },
    )
    client.post("/push", data=json.dumps(test_planning), content_type="application/json")

    data = get_json(client, '/agenda/search?filter={"coverage_status":["planned"]}')
    assert 1 == data["_meta"]["total"]
    assert "foo" == data["_items"][0]["_id"]

    data = get_json(client, '/agenda/search?filter={"coverage_status":["not intended"]}')
    assert 1 == data["_meta"]["total"]
    assert "bar" == data["_items"][0]["_id"]

    data = get_json(client, '/agenda/search?filter={"coverage_status":["may be"]}')
    assert 1 == data["_meta"]["total"]
    assert "123foo" == data["_items"][0]["_id"]

    data = get_json(client, '/agenda/search?filter={"coverage_status":["not planned"]}')
    assert 1 == data["_meta"]["total"]
    assert "baz" == data["_items"][0]["_id"]

    data = get_json(client, '/agenda/search?filter={"coverage_status":["completed"]}')
    assert 1 == data["_meta"]["total"]
    assert "123foo" == data["_items"][0]["_id"]


def test_filter_events_only(client):
    test_planning = {
        "description_text": "description here",
        "abstract": "abstract text",
        "_current_version": 1,
        "agendas": [],
        "anpa_category": [{"name": "Entertainment", "subject": "01000000", "qcode": "e"}],
        "item_id": "foo",
        "ednote": "ed note here",
        "slugline": "Vivid planning item",
        "headline": "Planning headline",
        "planning_date": "2018-05-28T10:51:52+0000",
        "state": "scheduled",
        "item_class": "plinat:newscoverage",
        "coverages": [
            {
                "planning": {
                    "g2_content_type": "text",
                    "slugline": "Vivid planning item",
                    "internal_note": "internal note here",
                    "genre": [{"name": "Article (news)", "qcode": "Article"}],
                    "ednote": "ed note here",
                    "scheduled": "2018-05-28T10:51:52+0000",
                },
                "news_coverage_status": {
                    "name": "coverage intended",
                    "label": "Planned",
                    "qcode": "ncostat:int",
                },
                "workflow_status": "draft",
                "firstcreated": "2018-05-28T10:55:00+0000",
                "coverage_id": "213",
            }
        ],
        "_id": "foo",
        "urgency": 3,
        "guid": "foo",
        "name": "This is the name of the vivid planning item",
        "subject": [{"name": "library and museum", "qcode": "01009000", "parent": "01000000"}],
        "pubstatus": "usable",
        "type": "planning",
    }

    client.post("/push", data=json.dumps(test_planning), content_type="application/json")
    data = get_json(client, "/agenda/search")
    assert 2 == data["_meta"]["total"]
    assert "urn:conference" == data["_items"][1]["_id"]
    assert "foo" == data["_items"][0]["_id"]
    assert 1 == len(data["_items"][1]["planning_items"])
    assert 1 == len(data["_items"][1]["coverages"])
    data = get_json(client, "/agenda/search?itemType=events")

    assert 1 == data["_meta"]["total"]
    assert "urn:conference" == data["_items"][0]["_id"]
    assert "planning_items" not in data["_items"][0]
    assert "coverages" not in data["_items"][0]


def test_agenda_filters_query(app):
    app.config.update(
        {
            "AGENDA_TIME_FILTERS": [
                {"name": "Next 7 days", "filter": "next_7_days", "query": "now+7d/d"},
                {"name": "Next 30 days", "filter": "next_30_days", "query": "now+30d/d"},
                {"name": "Next 3 months", "filter": "next_3_months", "query": "now+3M/d"},
                {"name": "Next 12 months", "filter": "next_12_months", "query": "now+12M/d", "default": True},
                {"name": "Last 7 days", "filter": "last_7_days", "query": "now-7d/d"},
                {"name": "Last 30 days", "filter": "last_30_days", "query": "now-30d/d"},
                {"name": "Last 24 hours", "filter": "last_24_hours", "query": "now-24h/h"},
                {"name": "Today", "query": "now/d", "filter": "today"},
                {"name": "This Week", "query": "now/w", "filter": "this_week"},
                {"name": "This Month", "query": "now/M", "filter": "this_month"},
            ]
        }
    )

    now = datetime.now(pytz.UTC)

    # Test case 1: Filter for next_3_months with date_from 2024-08-12
    args = {"date_from": "2024-08-12", "date_filter": "next_3_months"}
    date_range = get_date_filters(args)
    assert date_range["gt"] == datetime(2024, 8, 12, 0, 0, tzinfo=pytz.UTC)
    assert date_range["lt"] == datetime(2024, 8, 12, 0, 0, tzinfo=pytz.UTC) + timedelta(days=90)

    # Test case 2: Filter for last_7_days with date_from 2024-08-12
    args = {"date_from": now.strftime("%Y-%m-%d"), "date_filter": "last_7_days"}
    date_range = get_date_filters(args)
    assert date_range["gt"] == datetime.combine(now, datetime.min.time(), tzinfo=pytz.UTC) - timedelta(days=7)
    assert date_range["lt"] == datetime.combine(now, datetime.min.time(), tzinfo=pytz.UTC)

    # Test case 3: Custom filter with date_from 2024-08-12 and date_to 2024-09-12
    args = {"date_from": "2024-08-12", "date_filter": "custom_date", "date_to": "2024-09-12"}
    date_range = get_date_filters(args)
    assert date_range["gt"] == datetime(2024, 8, 12, 0, 0, tzinfo=pytz.UTC)
    assert date_range["lt"] == datetime(2024, 9, 12, 23, 59, 59, tzinfo=pytz.UTC)

    # Test case 4: Default case where default filter is "next_12_months"
    args = {"date_from": "2024-08-12"}
    date_range = get_date_filters(args)
    assert date_range["gt"] == datetime(2024, 8, 12, 0, 0, tzinfo=pytz.UTC)
    assert date_range["lt"] == datetime(2025, 8, 12, 0, 0, tzinfo=pytz.UTC)

    # Test case 5: Filter for this_week
    args = {"date_from": "2024-08-13", "date_filter": "today"}
    date_range = get_date_filters(args)
    assert date_range["gt"] == datetime(2024, 8, 13, 0, 0, tzinfo=pytz.UTC)
    assert date_range["lt"] == datetime(2024, 8, 13, 23, 59, 59, tzinfo=pytz.UTC)
