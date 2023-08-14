from typing import Dict, Any, List
from flask import json
from flask.testing import FlaskClient

from newsroom.factory.app import BaseNewsroomApp
from newsroom.agenda.agenda import AgendaResource, aggregations as agenda_aggregations
from newsroom.wire.search import (
    WireSearchResource,
    get_aggregations as get_wire_aggregations,
)
from newsroom.search.config import init_nested_aggregation
from newsroom.utils import deep_get
from newsroom.tests.conftest import reset_elastic


test_event_1 = {
    "guid": "event1",
    "type": "event",
    "state": "scheduled",
    "pubstatus": "usable",
    "slugline": "New Press Conference",
    "name": "Prime minister press conference",
    "subject": [
        {
            "qcode": "1523",
            "name": "Test Subject",
        },
        {
            "qcode": "abcd",
            "name": "Sports",
            "scheme": "something completely different",
        },
    ],
    "dates": {
        "start": "2038-05-28T04:00:00+0000",
        "end": "2038-05-28T05:00:00+0000",
        "tz": "Australia/Sydney",
    },
}

test_event_2 = {
    "guid": "event2",
    "type": "event",
    "state": "scheduled",
    "pubstatus": "usable",
    "slugline": "New Press Conference",
    "name": "Prime minister press conference",
    "subject": [
        {
            "qcode": "1523",
            "name": "Test Subject",
        },
        {"qcode": "abcd", "name": "Sports", "scheme": "sttdepartment"},
    ],
    "dates": {
        "start": "2038-05-28T04:00:00+0000",
        "end": "2038-05-28T05:00:00+0000",
        "tz": "Australia/Sydney",
    },
}

test_wire_item_1 = {
    "guid": "foo1",
    "type": "text",
    "headline": "Foo",
    "firstcreated": "2017-11-27T08:00:57+0000",
    "body_html": "<p>foo bar</p>",
    "genre": [{"name": "News", "code": "news"}],
    "subject": [
        {
            "qcode": "1523",
            "name": "Test Subject",
        }
    ],
}

test_wire_item_2 = {
    "guid": "foo2",
    "type": "text",
    "headline": "Foo",
    "firstcreated": "2017-11-27T08:00:57+0000",
    "body_html": "<p>foo bar</p>",
    "genre": [{"name": "News", "code": "news"}],
    "subject": [
        {
            "qcode": "1523",
            "name": "Test Subject",
        },
        {"qcode": "abcd", "name": "Sporting Event", "scheme": "distribution"},
    ],
}


def get_agg_keys(data: Dict[str, Any], path: str) -> List[str]:
    return [bucket.get("key") for bucket in deep_get(data, f"_aggregations.{path}.buckets", [])]


def test_default_agenda_groups_config(app: BaseNewsroomApp, client: FlaskClient):
    """Tests the default config (disabled nested search groups)"""

    assert len(app.config["AGENDA_GROUPS"]) == 4

    group_fields = [group.get("field") for group in app.config["AGENDA_GROUPS"]]
    assert "service" in group_fields
    assert "subject" in group_fields
    assert "urgency" in group_fields
    assert "place" in group_fields

    assert agenda_aggregations["subject"] == {"terms": {"field": "subject.name", "size": 20}}

    # Test search agenda_aggregations
    client.post("/push", data=json.dumps(test_event_1), content_type="application/json")
    resp = client.get("/agenda/search")
    data = json.loads(resp.get_data())
    assert get_agg_keys(data, "subject") == ["Sports", "Test Subject"]


def test_custom_agenda_groups_config(app: BaseNewsroomApp, client: FlaskClient):
    """Tests custom config, enabling nested search groups"""

    app.config["AGENDA_GROUPS"].append(
        {
            "field": "sttdepartment",
            "label": "Department",
            "nested": {
                "parent": "subject",
                "field": "scheme",
                "value": "sttdepartment",
                "include_planning": True,
            },
        }
    )
    init_nested_aggregation(AgendaResource, app.config["AGENDA_GROUPS"], agenda_aggregations)
    reset_elastic(app)

    # Test if the Eve & agenda_aggregations config has been updated

    # Test generated/modified aggregation configs
    # Parent field
    assert agenda_aggregations["subject"] == {
        "nested": {"path": "subject"},
        "aggs": {
            "subject_filtered": {
                "filter": {"bool": {"must_not": [{"terms": {"subject.scheme": ["sttdepartment"]}}]}},
                "aggs": {"subject": {"terms": {"field": "subject.name", "size": 20}}},
            },
        },
    }

    # Nested Field
    assert agenda_aggregations["sttdepartment"] == {
        "nested": {"path": "subject"},
        "aggs": {
            "sttdepartment_filtered": {
                "filter": {"bool": {"filter": [{"term": {"subject.scheme": "sttdepartment"}}]}},
                "aggs": {"sttdepartment": {"terms": {"field": "subject.name", "size": 20}}},
            },
        },
    }
    assert agenda_aggregations["sttdepartment_planning"] == {
        "nested": {"path": "planning_items"},
        "aggs": {
            "sttdepartment": {
                "nested": {"path": "planning_items.subject"},
                "aggs": {
                    "sttdepartment_filtered": {
                        "filter": {"bool": {"filter": [{"term": {"planning_items.subject.scheme": "sttdepartment"}}]}},
                        "aggs": {
                            "sttdepartment": {
                                "terms": {
                                    "field": "planning_items.subject.name",
                                    "size": 20,
                                }
                            }
                        },
                    }
                },
            }
        },
    }

    # Test search agenda_aggregations
    client.post("/push", data=json.dumps(test_event_1), content_type="application/json")
    client.post("/push", data=json.dumps(test_event_2), content_type="application/json")
    resp = client.get("/agenda/search")
    data = json.loads(resp.get_data())
    assert get_agg_keys(data, "subject.subject_filtered.subject") == ["Test Subject", "Sports"]
    assert get_agg_keys(data, "sttdepartment.sttdepartment_filtered.sttdepartment") == ["Sports"]

    # Search using the new search group, ``sttdepartment==Sports``
    resp = client.get("/agenda/search?filter=%7B%22sttdepartment%22%3A%5B%22Sports%22%5D%7D")
    data = json.loads(resp.get_data())
    assert len(data["_items"]) == 1, [item["_id"] for item in data["_items"]]
    assert data["_items"][0]["_id"] == "event2"


def test_default_wire_groups_config(app: BaseNewsroomApp, client: FlaskClient):
    """Tests the default wire config (disabled nested search groups)"""

    assert len(app.config["WIRE_GROUPS"]) == 5

    group_fields = [group.get("field") for group in app.config["WIRE_GROUPS"]]
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
    assert get_agg_keys(data, "subject") == ["Test Subject"]


def test_custom_wire_groups_config(app: BaseNewsroomApp, client: FlaskClient):
    """Tests custom wire config, enabling nested search groups"""

    app.config["WIRE_GROUPS"].append(
        {
            "field": "distribution",
            "label": "Distribution",
            "nested": {"parent": "subject", "field": "scheme", "value": "distribution"},
        }
    )
    wire_aggregations = get_wire_aggregations()
    init_nested_aggregation(WireSearchResource, app.config["WIRE_GROUPS"], wire_aggregations)
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
                "filter": {"bool": {"filter": [{"term": {"subject.scheme": "distribution"}}]}},
                "aggs": {"distribution": {"terms": {"field": "subject.name", "size": 20}}},
            },
        },
    }

    # Test search wire_aggregations
    client.post("/push", data=json.dumps(test_wire_item_1), content_type="application/json")
    client.post("/push", data=json.dumps(test_wire_item_2), content_type="application/json")
    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())

    assert get_agg_keys(data, "subject.subject_filtered.subject") == ["Test Subject"]
    assert get_agg_keys(data, "distribution.distribution_filtered.distribution") == ["Sporting Event"]

    # Search using the new search group, ``distribution==Sporting Event``
    resp = client.get("/wire/search?filter=%7B%22distribution%22%3A%5B%22Sporting%20Event%22%5D%7D")
    data = json.loads(resp.get_data())
    assert len(data["_items"]) == 1
    assert data["_items"][0]["_id"] == "foo2"
