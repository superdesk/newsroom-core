from flask import json
from time import sleep
from datetime import datetime, timedelta
from eve.utils import ParsedRequest
from bson import ObjectId

from newsroom.mongo_utils import (
    index_elastic_from_mongo,
    index_elastic_from_mongo_from_timestamp,
)
from newsroom.wire.search import (
    WireSearchResource,
    get_aggregations as get_wire_aggregations,
)
from newsroom.search.config import init_nested_aggregation
from newsroom.commands import fix_topic_nested_filters

from newsroom.tests.conftest import reset_elastic
from ..fixtures import items, init_items, init_auth, init_company  # noqa


def remove_elastic_index(app):
    # remove the elastic index
    indices = "%s*" % app.config["CONTENTAPI_ELASTICSEARCH_INDEX"]
    es = app.data.elastic.es
    es.indices.delete(indices, ignore=[404])


def test_item_detail(app, client):
    remove_elastic_index(app)
    app.data.init_elastic(app)
    sleep(1)
    index_elastic_from_mongo()
    sleep(1)

    resp = client.get("/wire/tag:foo")
    assert resp.status_code == 200
    html = resp.get_data().decode("utf-8")
    assert "Amazon Is Opening More Bookstores" in html

    resp = client.get("/wire/%s/versions" % items[1]["_id"])
    data = json.loads(resp.get_data())
    assert 2 == len(data["_items"])
    assert "tag:weather" == data["_items"][0]["_id"]

    resp = client.get("/wire/search")
    assert resp.status_code == 200
    data = json.loads(resp.get_data())
    assert 3 == len(data["_items"])


def test_index_from_mongo_hours_from(app, client):
    remove_elastic_index(app)
    app.data.init_elastic(app)
    sleep(1)
    index_elastic_from_mongo(hours=24)
    sleep(1)

    resp = client.get("/wire/tag:foo")
    assert resp.status_code == 200
    html = resp.get_data().decode("utf-8")
    assert "Amazon Is Opening More Bookstores" in html

    resp = client.get("/wire/search")
    assert resp.status_code == 200
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])


def test_index_from_mongo_collection(app, client):
    remove_elastic_index(app)
    app.data.init_elastic(app)
    sleep(1)
    index_elastic_from_mongo(collection="items")
    sleep(1)

    resp = client.get("/wire/tag:foo")
    assert resp.status_code == 200
    html = resp.get_data().decode("utf-8")
    assert "Amazon Is Opening More Bookstores" in html

    resp = client.get("/wire/search")
    assert resp.status_code == 200
    data = json.loads(resp.get_data())
    assert 3 == len(data["_items"])


def test_index_from_mongo_from_timestamp(app, client):
    app.data.remove("items")
    sorted_items = [
        {
            "_id": "tag:foo-1",
            "_created": datetime.now() - timedelta(hours=5),
        },
        {"_id": "urn:bar-1", "_created": datetime.now() - timedelta(hours=5)},
        {"_id": "tag:foo-2", "_created": datetime.now() - timedelta(hours=4)},
        {"_id": "urn:bar-2", "_created": datetime.now() - timedelta(hours=4)},
        {"_id": "tag:foo-3", "_created": datetime.now() - timedelta(hours=3)},
        {"_id": "urn:bar-3", "_created": datetime.now() - timedelta(hours=3)},
    ]

    app.data.insert("items", sorted_items)
    remove_elastic_index(app)
    app.data.init_elastic(app)
    sleep(1)
    assert 0 == app.data.elastic.find("items", ParsedRequest(), {})[1]

    timestamp = (datetime.now() - timedelta(hours=3, minutes=5)).strftime("%Y-%m-%dT%H:%M")
    index_elastic_from_mongo_from_timestamp("items", timestamp, "older")
    sleep(1)
    assert 4 == app.data.elastic.find("items", ParsedRequest(), {})[1]

    index_elastic_from_mongo_from_timestamp("items", timestamp, "newer")
    sleep(1)
    assert 6 == app.data.elastic.find("items", ParsedRequest(), {})[1]


def test_fix_topic_nested_filters(app, client):
    app.config["WIRE_GROUPS"].extend(
        [
            {
                "field": "distribution",
                "label": "Distribution",
                "nested": {
                    "parent": "subject",
                    "field": "scheme",
                    "value": "distribution",
                },
            },
            {
                "field": "subject_custom",
                "label": "Index",
                "nested": {
                    "parent": "subject",
                    "field": "scheme",
                    "value": "subject_custom",
                },
            },
        ]
    )
    app.config["WIRE_GROUPS"] = [
        config_group for config_group in app.config["WIRE_GROUPS"] if config_group["field"] != "subject"
    ]
    init_nested_aggregation(WireSearchResource, app.config["WIRE_GROUPS"], get_wire_aggregations())
    reset_elastic(app)

    app.data.insert(
        "items",
        [
            {
                "_id": "foo",
                "headline": "item headline",
                "subject": [
                    {
                        "code": "QuickHit",
                        "name": "QuickHit",
                        "scheme": "distribution",
                    },
                    {
                        "code": "Print / Broadcast",
                        "name": "Print / Broadcast",
                        "scheme": "distribution",
                    },
                    {
                        "code": "01000000",
                        "name": "arts, culture, entertainment and media",
                        "scheme": "subject_custom",
                    },
                ],
            }
        ],
    )
    topic_id = ObjectId()
    app.data.insert(
        "topics",
        [
            {
                "_id": topic_id,
                "label": "Foo",
                "topic_type": "wire",
                "filter": {
                    "subject": [
                        "QuickHit",
                        "Print / Broadcast",
                        "arts, culture, entertainment and media",
                    ],
                },
            }
        ],
    )

    with app.test_request_context():
        fix_topic_nested_filters()

    updated_topic = app.data.find_one("topics", None, topic_id)

    assert "subject" not in updated_topic["filter"]
    assert len(updated_topic["filter"]["distribution"]) == 2
    assert "QuickHit" in updated_topic["filter"]["distribution"]
    assert "Print / Broadcast" in updated_topic["filter"]["distribution"]
    assert len(updated_topic["filter"]["subject_custom"]) == 1
    assert "arts, culture, entertainment and media" in updated_topic["filter"]["subject_custom"]
