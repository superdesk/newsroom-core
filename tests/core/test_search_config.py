from flask import json
from flask.testing import FlaskClient

from newsroom.factory.app import BaseNewsroomApp
from newsroom.agenda.agenda import AgendaResource, aggregations as agenda_aggregations
from newsroom.wire.search import WireSearchResource, get_aggregations as get_wire_aggregations
from newsroom.search_config import init_nested_aggregation
from newsroom.tests.conftest import reset_elastic


test_event_1 = {
    "guid": "event1",
    "type": "event",
    "state": "scheduled",
    "pubstatus": "usable",
    "slugline": "New Press Conference",
    "name": "Prime minister press conference",
    "subject": [{
        "qcode": "1523",
        "name": "Test Subject",
    }],
    "dates": {
        "start": "2038-05-28T04:00:00+0000",
        "end": "2038-05-28T05:00:00+0000",
        "tz": "Australia/Sydney"
    }
}

test_event_2 = {
    "guid": "event2",
    "type": "event",
    "state": "scheduled",
    "pubstatus": "usable",
    "slugline": "New Press Conference",
    "name": "Prime minister press conference",
    "subject": [{
        "qcode": "1523",
        "name": "Test Subject",
    }, {
        "qcode": "abcd",
        "name": "Sporting Event",
        "scheme": "event_type"
    }],
    "dates": {
        "start": "2038-05-28T04:00:00+0000",
        "end": "2038-05-28T05:00:00+0000",
        "tz": "Australia/Sydney"
    }
}

test_wire_item_1 = {
    "guid": "foo1",
    "type": "text",
    "headline": "Foo",
    "firstcreated": "2017-11-27T08:00:57+0000",
    "body_html": "<p>foo bar</p>",
    "genre": [{"name": "News", "code": "news"}],
    "subject": [{
        "qcode": "1523",
        "name": "Test Subject",
    }],
}

test_wire_item_2 = {
    "guid": "foo2",
    "type": "text",
    "headline": "Foo",
    "firstcreated": "2017-11-27T08:00:57+0000",
    "body_html": "<p>foo bar</p>",
    "genre": [{"name": "News", "code": "news"}],
    "subject": [{
        "qcode": "1523",
        "name": "Test Subject",
    }, {
        "qcode": "abcd",
        "name": "Sporting Event",
        "scheme": "distribution"
    }],
}


def test_default_agenda_groups_config(app: BaseNewsroomApp, client: FlaskClient):
    """Tests the default config (disabled nested search groups)"""

    assert len(app.config["AGENDA_GROUPS"]) == 4

    group_fields = [
        group.get("field")
        for group in app.config["AGENDA_GROUPS"]
    ]
    assert "service" in group_fields
    assert "subject" in group_fields
    assert "urgency" in group_fields
    assert "place" in group_fields

    assert agenda_aggregations["subject"] == {"terms": {"field": "subject.name", "size": 20}}

    # Test search agenda_aggregations
    client.post("/push", data=json.dumps(test_event_1), content_type="application/json")
    resp = client.get("/agenda/search")
    data = json.loads(resp.get_data())
    assert data["_aggregations"]["subject"] == {
        "doc_count_error_upper_bound": 0,
        "sum_other_doc_count": 0,
        "buckets": [{
            "doc_count": 1,
            "key": "Test Subject",
        }]
    }


def test_custom_agenda_groups_config(app: BaseNewsroomApp, client: FlaskClient):
    """Tests custom config, enabling nested search groups"""

    app.config["AGENDA_GROUPS"].append({
        "field": "event_type",
        "label": "Event Type",
        "nested": {
            "parent": "subject",
            "field": "scheme",
            "value": "event_type",
        },
    })
    init_nested_aggregation(
        AgendaResource,
        app.config["AGENDA_GROUPS"],
        agenda_aggregations
    )
    reset_elastic(app)

    # Test if the Eve & agenda_aggregations config has been updated

    # Test generated/modified aggregation configs
    # Parent field
    assert agenda_aggregations["subject"] == {
        "nested": {"path": "subject"},
        "aggs": {
            "subject_filtered": {
                "filter": {"bool": {"must_not": [{"terms": {"subject.scheme": ["event_type"]}}]}},
                "aggs": {"subject": {"terms": {"field": "subject.name", "size": 20}}},
            },
        },
    }

    # Nested Field
    assert agenda_aggregations["event_type"] == {
        "nested": {"path": "subject"},
        "aggs": {
            "event_type_filtered": {
                "filter": {"bool": {"must": [{"term": {"subject.scheme": "event_type"}}]}},
                "aggs": {"event_type": {"terms": {"field": "subject.name", "size": 20}}},
            },
        },
    }

    # Test search agenda_aggregations
    client.post("/push", data=json.dumps(test_event_1), content_type="application/json")
    client.post("/push", data=json.dumps(test_event_2), content_type="application/json")
    resp = client.get("/agenda/search")
    data = json.loads(resp.get_data())
    assert data["_aggregations"]["subject"] == {
        "doc_count": 3,
        "subject_filtered": {
            "doc_count": 2,
            "subject": {
                "doc_count_error_upper_bound": 0,
                "sum_other_doc_count": 0,
                "buckets": [{
                    "doc_count": 2,
                    "key": "Test Subject",
                }],
            },
        },
    }
    assert data["_aggregations"]["event_type"] == {
        "doc_count": 3,
        "event_type_filtered": {
            "doc_count": 1,
            "event_type": {
                "doc_count_error_upper_bound": 0,
                "sum_other_doc_count": 0,
                "buckets": [{
                    "doc_count": 1,
                    "key": "Sporting Event",
                }],
            },
        },
    }

    # Search using the new search group, ``event_type==Sporting Event``
    resp = client.get("/agenda/search?filter=%7B%22event_type%22%3A%5B%22Sporting%20Event%22%5D%7D")
    data = json.loads(resp.get_data())
    assert len(data["_items"]) == 1
    assert data["_items"][0]["_id"] == "event2"


def test_default_wire_groups_config(app: BaseNewsroomApp, client: FlaskClient):
    """Tests the default wire config (disabled nested search groups)"""

    assert len(app.config["WIRE_GROUPS"]) == 5

    group_fields = [
        group.get("field")
        for group in app.config["WIRE_GROUPS"]
    ]
    assert "service" in group_fields
    assert "subject" in group_fields
    assert "genre" in group_fields
    assert "urgency" in group_fields
    assert "place" in group_fields

    wire_aggregations = get_wire_aggregations()
    assert wire_aggregations["subject"] == {"terms": {"field": "subject.name", "size": 20}}

    client.post("/push", data=json.dumps(test_wire_item_1), content_type="application/json")
    res = client.get("/wire/search")
    data = json.loads(res.get_data())
    assert data["_aggregations"]["subject"] == {
        "doc_count_error_upper_bound": 0,
        "sum_other_doc_count": 0,
        "buckets": [{
            "doc_count": 1,
            "key": "Test Subject",
        }]
    }


def test_custom_wire_groups_config(app: BaseNewsroomApp, client: FlaskClient):
    """Tests custom wire config, enabling nested search groups"""

    app.config["WIRE_GROUPS"].append({
        "field": "distribution",
        "label": "Distribution",
        "nested": {
            "parent": "subject",
            "field": "scheme",
            "value": "distribution"
        },
    })
    wire_aggregations = get_wire_aggregations()
    init_nested_aggregation(
        WireSearchResource,
        app.config["WIRE_GROUPS"],
        wire_aggregations
    )
    reset_elastic(app)

    # Test generated/modified aggregation configs
    # Parent field
    assert wire_aggregations["subject"] == {
        "nested": {"path": "subject"},
        "aggs": {
            "subject_filtered": {
                "filter": {"bool": {"must_not": [{"terms": {"subject.scheme": ["distribution"]}}]}},
                "aggs": {"subject": {"terms": {"field": "subject.name", "size": 20}}},
            },
        },
    }

    # Nested Field
    assert wire_aggregations["distribution"] == {
        "nested": {"path": "subject"},
        "aggs": {
            "distribution_filtered": {
                "filter": {"bool": {"must": [{"term": {"subject.scheme": "distribution"}}]}},
                "aggs": {"distribution": {"terms": {"field": "subject.name", "size": 20}}},
            },
        },
    }

    # Test search wire_aggregations
    client.post("/push", data=json.dumps(test_wire_item_1), content_type="application/json")
    client.post("/push", data=json.dumps(test_wire_item_2), content_type="application/json")
    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())
    assert data["_aggregations"]["subject"] == {
        "doc_count": 3,
        "subject_filtered": {
            "doc_count": 2,
            "subject": {
                "doc_count_error_upper_bound": 0,
                "sum_other_doc_count": 0,
                "buckets": [{
                    "doc_count": 2,
                    "key": "Test Subject",
                }],
            },
        },
    }
    assert data["_aggregations"]["distribution"] == {
        "doc_count": 3,
        "distribution_filtered": {
            "doc_count": 1,
            "distribution": {
                "doc_count_error_upper_bound": 0,
                "sum_other_doc_count": 0,
                "buckets": [{
                    "doc_count": 1,
                    "key": "Sporting Event",
                }],
            },
        },
    }

    # Search using the new search group, ``distribution==Sporting Event``
    resp = client.get("/wire/search?filter=%7B%22distribution%22%3A%5B%22Sporting%20Event%22%5D%7D")
    data = json.loads(resp.get_data())
    assert len(data["_items"]) == 1
    assert data["_items"][0]["_id"] == "foo2"
