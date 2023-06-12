import pytz
from flask import json, g, session as server_session
from datetime import datetime, timedelta
from urllib import parse
from bson import ObjectId
from copy import deepcopy

from ..fixtures import (  # noqa: F401
    items,
    init_items,
    init_auth,
    init_company,
    PUBLIC_USER_ID,
    COMPANY_1_ID,
)
from ..utils import get_json, get_admin_user_id, mock_send_email
from unittest import mock
from newsroom.tests.users import ADMIN_USER_ID
from superdesk import get_resource_service


NAV_1 = ObjectId("5e65964bf5db68883df561c0")
NAV_2 = ObjectId("5e65964bf5db68883df561c1")


def test_item_detail(client):
    resp = client.get("/wire/tag:foo")
    assert resp.status_code == 200
    html = resp.get_data().decode("utf-8")
    assert "Amazon Is Opening More Bookstores" in html


def test_item_json(client):
    resp = client.get("/wire/tag:foo?format=json")
    data = json.loads(resp.get_data())
    assert "headline" in data


@mock.patch("newsroom.email.send_email", mock_send_email)
def test_share_items(client, app):
    user_ids = app.data.insert(
        "users",
        [
            {
                "email": "foo2@bar.com",
                "first_name": "Foo",
                "last_name": "Bar",
                "receive_email": True,
                "receive_app_notifications": True,
            }
        ],
    )

    with app.mail.record_messages() as outbox:
        resp = client.post(
            "/wire_share",
            data=json.dumps(
                {
                    "items": [item["_id"] for item in items],
                    "users": [str(user_ids[0])],
                    "message": "Some info message",
                }
            ),
            content_type="application/json",
        )

        assert resp.status_code == 201, resp.get_data().decode("utf-8")
        assert len(outbox) == 1
        assert outbox[0].recipients == ["foo2@bar.com"]
        assert outbox[0].sender == "newsroom@localhost"
        assert outbox[0].subject == "From AAP Newsroom: %s" % items[0]["headline"]
        assert "Hi Foo Bar" in outbox[0].body
        assert "admin admin (admin@sourcefabric.org) shared " in outbox[0].body
        assert items[0]["headline"] in outbox[0].body
        assert items[1]["headline"] in outbox[0].body
        assert "http://localhost:5050/wire?item=%s" % parse.quote(items[0]["_id"]) in outbox[0].body
        assert "http://localhost:5050/wire?item=%s" % parse.quote(items[1]["_id"]) in outbox[0].body
        # assert 'Some info message' in outbox[0].body

    resp = client.get("/wire/{}?format=json".format(items[0]["_id"]))
    data = json.loads(resp.get_data())
    assert "shares" in data

    user_id = get_admin_user_id(app)
    assert str(user_id) in data["shares"]


def get_bookmarks_count(client, user):
    resp = client.get("/api/wire_search?bookmarks=%s" % str(user))
    assert resp.status_code == 200
    data = json.loads(resp.get_data())
    return data["_meta"]["total"]


def test_bookmarks(client, app):
    user_id = get_admin_user_id(app)
    assert user_id

    assert 0 == get_bookmarks_count(client, user_id)

    resp = client.post(
        "/wire_bookmark",
        data=json.dumps(
            {
                "items": [items[0]["_id"]],
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 200

    assert 1 == get_bookmarks_count(client, user_id)

    client.delete(
        "/wire_bookmark",
        data=json.dumps(
            {
                "items": [items[0]["_id"]],
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 200

    assert 0 == get_bookmarks_count(client, user_id)


def test_bookmarks_by_section(client, app):
    products = [
        {
            "_id": 1,
            "name": "Service A",
            "query": "service.code: a",
            "is_enabled": True,
            "description": "Service A",
            "companies": [COMPANY_1_ID],
            "sd_product_id": None,
            "product_type": "wire",
        }
    ]

    app.data.insert("products", products)
    product_id = app.data.find_all("products")[0]["_id"]
    assert product_id == 1

    with client.session_transaction() as session:
        session["user"] = "59b4c5c61d41c8d736852fbf"
        session["user_type"] = "public"

    assert 0 == get_bookmarks_count(client, PUBLIC_USER_ID)

    resp = client.post(
        "/wire_bookmark",
        data=json.dumps(
            {
                "items": [items[0]["_id"]],
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 200

    assert 1 == get_bookmarks_count(client, PUBLIC_USER_ID)

    client.delete(
        "/wire_bookmark",
        data=json.dumps(
            {
                "items": [items[0]["_id"]],
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 200

    assert 0 == get_bookmarks_count(client, PUBLIC_USER_ID)


def test_item_copy(client, app):
    resp = client.post("/wire/{}/copy".format(items[0]["_id"]), content_type="application/json")
    assert resp.status_code == 200

    resp = client.get("/wire/tag:foo?format=json")
    data = json.loads(resp.get_data())
    assert "copies" in data

    user_id = get_admin_user_id(app)
    assert str(user_id) in data["copies"]


def test_versions(client, app):
    resp = client.get("/wire/%s/versions" % items[0]["_id"])
    assert 200 == resp.status_code
    data = json.loads(resp.get_data())
    assert len(data.get("_items")) == 0

    resp = client.get("/wire/%s/versions" % items[1]["_id"])
    data = json.loads(resp.get_data())
    assert 2 == len(data["_items"])
    assert "tag:weather" == data["_items"][0]["_id"]
    assert "AAP" == data["_items"][0]["source"]
    assert "c" == data["_items"][1]["service"][0]["code"]


def test_search_filters_items_with_updates(client, app):
    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())
    assert 3 == len(data["_items"])
    assert "tag:weather" not in [item["_id"] for item in data["_items"]]


def test_search_includes_killed_items(client, app):
    app.data.insert("items", [{"_id": "foo", "pubstatus": "canceled", "headline": "killed"}])
    resp = client.get("/wire/search?q=headline:killed")
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])


def test_search_by_products_id(client, app):
    app.data.insert(
        "items",
        [{"_id": "foo", "headline": "product test", "products": [{"code": "12345"}]}],
    )
    resp = client.get("/wire/search?q=products.code:12345")
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])


def test_search_filter_by_category(client, app):
    resp = client.get("/wire/search?filter=%s" % json.dumps({"service": ["Service A"]}))
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])


def test_filter_by_product_anonymous_user_gets_all(client, app):
    resp = client.get("/wire/search?products=%s" % json.dumps({"10": True}))
    data = json.loads(resp.get_data())
    assert 3 == len(data["_items"])
    assert "_aggregations" in data


def test_logged_in_user_no_product_gets_no_results(client, app):
    with client.session_transaction() as session:
        session["user"] = str(PUBLIC_USER_ID)
        session["user_type"] = "public"
    resp = client.get("/wire/search")
    assert 403 == resp.status_code


def test_logged_in_user_no_company_gets_no_results(client, app):
    with client.session_transaction() as session:
        session["user"] = str(PUBLIC_USER_ID)
        session["user_type"] = "public"

    resp = client.get("/wire/search")
    assert resp.status_code == 403


def test_administrator_gets_all_results(client, app):
    with client.session_transaction() as session:
        session["user"] = ADMIN_USER_ID
        session["user_type"] = "administrator"

    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())
    assert 3 == len(data["_items"])


def test_search_filtered_by_users_products(client, app):
    app.data.insert(
        "products",
        [
            {
                "_id": 10,
                "name": "product test",
                "sd_product_id": 1,
                "companies": [COMPANY_1_ID],
                "is_enabled": True,
                "product_type": "wire",
            }
        ],
    )

    with client.session_transaction() as session:
        session["user"] = str(PUBLIC_USER_ID)
        session["user_type"] = "public"

    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])
    assert "_aggregations" in data


def test_search_filter_by_individual_navigation(client, app):
    app.data.insert(
        "navigations",
        [
            {
                "_id": NAV_1,
                "name": "navigation-1",
                "is_enabled": True,
                "product_type": "wire",
            },
            {
                "_id": NAV_2,
                "name": "navigation-2",
                "is_enabled": True,
                "product_type": "wire",
            },
        ],
    )

    app.data.insert(
        "products",
        [
            {
                "_id": 10,
                "name": "product test",
                "sd_product_id": 1,
                "companies": [COMPANY_1_ID],
                "navigations": [NAV_1],
                "product_type": "wire",
                "is_enabled": True,
            },
            {
                "_id": 11,
                "name": "product test 2",
                "sd_product_id": 2,
                "companies": [COMPANY_1_ID],
                "navigations": [NAV_2],
                "product_type": "wire",
                "is_enabled": True,
            },
        ],
    )
    with client.session_transaction() as session:
        session["user"] = str(PUBLIC_USER_ID)
        session["user_type"] = "public"

    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())
    assert 2 == len(data["_items"])
    assert "_aggregations" in data
    resp = client.get(f"/wire/search?navigation={NAV_1}")
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])
    assert "_aggregations" in data

    # test admin user filtering
    with client.session_transaction() as session:
        session["user"] = ADMIN_USER_ID
        session["user_type"] = "administrator"

    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())
    assert 3 == len(data["_items"])  # gets all by default

    resp = client.get(f"/wire/search?navigation={NAV_1}")
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])


def test_search_filtered_by_query_product(client, app):
    app.data.insert(
        "navigations",
        [
            {
                "_id": NAV_1,
                "name": "navigation-1",
                "is_enabled": True,
                "product_type": "wire",
            },
            {
                "_id": NAV_2,
                "name": "navigation-2",
                "is_enabled": True,
                "product_type": "wire",
            },
        ],
    )

    app.data.insert(
        "products",
        [
            {
                "_id": 12,
                "name": "product test",
                "query": "headline:more",
                "companies": [COMPANY_1_ID],
                "navigations": [NAV_1],
                "product_type": "wire",
                "is_enabled": True,
            },
            {
                "_id": 13,
                "name": "product test 2",
                "query": "headline:Weather",
                "companies": [COMPANY_1_ID],
                "navigations": [NAV_2],
                "product_type": "wire",
                "is_enabled": True,
            },
        ],
    )

    with client.session_transaction() as session:
        session["user"] = str(PUBLIC_USER_ID)
        session["user_type"] = "public"

    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())
    assert 2 == len(data["_items"])
    assert "_aggregations" in data
    resp = client.get(f"/wire/search?navigation={NAV_2}")
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])
    assert "_aggregations" in data


def test_search_pagination(client):
    resp = client.get("/wire/search?from=25")
    assert 200 == resp.status_code
    data = json.loads(resp.get_data())
    assert 0 == len(data["_items"])
    assert "_aggregations" not in data

    resp = client.get("/wire/search?from=2000")
    assert 400 == resp.status_code


def test_search_created_from(client):
    resp = client.get("/wire/search?created_from=now/d")
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])

    resp = client.get("/wire/search?created_from=now/w")
    data = json.loads(resp.get_data())
    assert 1 <= len(data["_items"])

    resp = client.get("/wire/search?created_from=now/M")
    data = json.loads(resp.get_data())

    assert 1 <= len(data["_items"])


def test_search_created_to(client):
    resp = client.get("/wire/search?created_to=%s" % datetime.now().strftime("%Y-%m-%d"))
    data = json.loads(resp.get_data())
    assert 3 == len(data["_items"])

    resp = client.get(
        "/wire/search?created_to=%s&timezone_offset=%s"
        % ((datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"), -120)
    )
    data = json.loads(resp.get_data())
    assert 0 == len(data["_items"])


def test_item_detail_access(client, app):
    item_url = "/wire/%s" % items[0]["_id"]
    data = get_json(client, item_url)
    assert data["_access"]
    assert data["body_html"]

    # public user
    with client.session_transaction() as session:
        session["user"] = str(PUBLIC_USER_ID)
        session["user_type"] = "public"

    # no access by default
    data = get_json(client, item_url)
    assert not data["_access"]
    assert not data.get("body_html")

    # add product
    app.data.insert(
        "products",
        [
            {
                "_id": 10,
                "name": "matching product",
                "companies": [COMPANY_1_ID],
                "is_enabled": True,
                "product_type": "wire",
                "query": "slugline:%s" % items[0]["slugline"],
            }
        ],
    )

    # normal access
    data = get_json(client, item_url)
    assert data["_access"]
    assert data["body_html"]


def test_search_using_section_filter_for_public_user(client, app):
    app.data.insert(
        "navigations",
        [
            {
                "_id": NAV_1,
                "name": "navigation-1",
                "is_enabled": True,
                "product_type": "wire",
            },
            {
                "_id": NAV_2,
                "name": "navigation-2",
                "is_enabled": True,
                "product_type": "wire",
            },
        ],
    )

    app.data.insert(
        "products",
        [
            {
                "_id": 12,
                "name": "product test",
                "query": "headline:more",
                "companies": [COMPANY_1_ID],
                "navigations": [NAV_1],
                "is_enabled": True,
                "product_type": "wire",
            },
            {
                "_id": 13,
                "name": "product test 2",
                "query": "headline:Weather",
                "companies": [COMPANY_1_ID],
                "navigations": [NAV_2],
                "is_enabled": True,
                "product_type": "wire",
            },
        ],
    )

    with client.session_transaction() as session:
        session["user"] = str(PUBLIC_USER_ID)
        session["user_type"] = "public"

    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())
    assert 2 == len(data["_items"])
    assert "_aggregations" in data
    resp = client.get(f"/wire/search?navigation={NAV_2}")
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])
    assert "_aggregations" in data

    app.data.insert(
        "section_filters",
        [
            {
                "_id": "f-1",
                "name": "product test 2",
                "query": "headline:Weather",
                "is_enabled": True,
                "filter_type": "wire",
            }
        ],
    )

    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])

    resp = client.get(f"/wire/search?navigation={NAV_2}")
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])

    resp = client.get(f"/wire/search?navigation={NAV_1}")
    data = json.loads(resp.get_data())
    assert 0 == len(data["_items"])


def test_administrator_gets_results_based_on_section_filter(client, app):
    with client.session_transaction() as session:
        session["user"] = ADMIN_USER_ID
        session["user_type"] = "administrator"

    app.data.insert(
        "section_filters",
        [
            {
                "_id": "f-1",
                "name": "product test 2",
                "query": "headline:Weather",
                "is_enabled": True,
                "filter_type": "wire",
            }
        ],
    )

    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])


def test_time_limited_access(client, app):
    app.data.insert(
        "products",
        [
            {
                "_id": 10,
                "name": "product test",
                "query": "versioncreated:<=now-2d",
                "companies": [COMPANY_1_ID],
                "is_enabled": True,
                "product_type": "wire",
            }
        ],
    )

    with client.session_transaction() as session:
        session["user"] = "59b4c5c61d41c8d736852fbf"
        session["user_type"] = "public"

    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())
    assert 2 == len(data["_items"])
    print(data["_items"][0]["versioncreated"])

    g.settings["wire_time_limit_days"]["value"] = 1
    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())
    assert 0 == len(data["_items"])

    g.settings["wire_time_limit_days"]["value"] = 100
    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())
    assert 2 == len(data["_items"])

    g.settings["wire_time_limit_days"]["value"] = 1
    company = app.data.find_one("companies", req=None, _id=COMPANY_1_ID)
    app.data.update("companies", COMPANY_1_ID, {"archive_access": True}, company)
    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())
    assert 2 == len(data["_items"])


def test_company_type_filter(client, app):
    app.data.insert(
        "products",
        [
            {
                "_id": 10,
                "name": "product test",
                "query": "versioncreated:<=now-2d",
                "companies": [COMPANY_1_ID],
                "is_enabled": True,
                "product_type": "wire",
            }
        ],
    )

    with client.session_transaction() as session:
        session["user"] = str(PUBLIC_USER_ID)
        session["user_type"] = "public"

    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())
    assert 2 == len(data["_items"])

    app.config["COMPANY_TYPES"] = [
        dict(id="test", wire_must={"term": {"service.code": "b"}}),
    ]

    company = app.data.find_one("companies", req=None, _id=COMPANY_1_ID)
    app.data.update("companies", COMPANY_1_ID, {"company_type": "test"}, company)

    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])
    assert "WEATHER" == data["_items"][0]["slugline"]

    app.config["COMPANY_TYPES"] = [
        dict(id="test", wire_must_not={"term": {"service.code": "b"}}),
    ]

    resp = client.get("/wire/search")
    data = json.loads(resp.get_data())
    assert 1 == len(data["_items"])
    assert "WEATHER" != data["_items"][0]["slugline"]


def test_search_by_products_and_filtered_by_embargoe(client, app):
    with app.test_request_context():
        server_session["user"] = str(PUBLIC_USER_ID)
        server_session["user_type"] = "public"
        app.data.insert(
            "products",
            [
                {
                    "_id": 10,
                    "name": "product test",
                    "query": "headline:china",
                    "companies": [COMPANY_1_ID],
                    "is_enabled": True,
                    "product_type": "wire",
                }
            ],
        )

        # embargoed item is not fetched
        app.data.insert(
            "items",
            [
                {
                    "_id": "foo",
                    "headline": "china",
                    "embargoed": (datetime.now() + timedelta(days=10)).replace(tzinfo=pytz.UTC),
                    "products": [{"code": "10"}],
                }
            ],
        )

        items = get_resource_service("wire_search").get_product_items(10, 20)
        assert 1 == len(items)

        app.config["COMPANY_TYPES"] = [
            dict(id="test", wire_must_not={"range": {"embargoed": {"gte": "now"}}}),
        ]

        company = app.data.find_one("companies", req=None, _id=COMPANY_1_ID)
        app.data.update("companies", COMPANY_1_ID, {"company_type": "test"}, company)

        items = get_resource_service("wire_search").get_product_items(10, 20)
        assert 0 == len(items)

        # ex-embargoed item is fetched
        app.data.insert(
            "items",
            [
                {
                    "_id": "bar",
                    "headline": "china story",
                    "embargoed": (datetime.now() - timedelta(days=10)).replace(tzinfo=pytz.UTC),
                    "products": [{"code": "10"}],
                }
            ],
        )

        items = get_resource_service("wire_search").get_product_items(10, 20)
        assert 1 == len(items)
        assert items[0]["headline"] == "china story"


def test_wire_delete(client, app):
    docs = [
        items[1],
        items[3],
        items[4],
    ]
    versions = [
        deepcopy(items[1]),
        deepcopy(items[3]),
        deepcopy(items[4]),
    ]

    versions[0].update(
        {
            "_id": ObjectId(),
            "_id_document": docs[0]["_id"],
        }
    )
    versions[1].update(
        {
            "_id": ObjectId(),
            "_id_document": docs[1]["_id"],
        }
    )
    versions[2].update(
        {
            "_id": ObjectId(),
            "_id_document": docs[2]["_id"],
        }
    )

    app.data.insert("items_versions", versions)

    for doc in docs:
        assert get_resource_service("items").find_one(req=None, _id=doc["_id"]) is not None
        assert get_resource_service("items_versions").find_one(req=None, _id_document=doc["_id"]) is not None

    resp = client.delete(
        "/wire",
        data=json.dumps(
            {
                "items": [docs[0]["_id"]],
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 200

    for doc in docs:
        assert get_resource_service("items").find_one(req=None, _id=doc["_id"]) is None
        assert get_resource_service("items_versions").find_one(req=None, _id_document=doc["_id"]) is None


def test_highlighting(client, app):
    app.data.insert(
        "items",
        [
            {
                "_id": "foo",
                "body_html": "Story that involves cheese and onions",
                "slugline": "That's the test slugline cheese",
                "headline": "Demo Article",
            }
        ],
    )
    resp = client.get("/wire/search?q=cheese&es_highlight=1")
    data = json.loads(resp.get_data())
    assert (
        data["_items"][0]["es_highlight"]["body_html"][0] == 'Story that involves <span class="es-highlight">'
        "cheese</span> and onions"
    )
    assert (
        data["_items"][0]["es_highlight"]["slugline"][0]
        == 'That\'s the test slugline <span class="es-highlight">cheese</span>'
    )

    resp = client.get("/wire/search?q=demo&es_highlight=1")
    data = json.loads(resp.get_data())
    assert data["_items"][0]["es_highlight"]["headline"][0] == '<span class="es-highlight">Demo</span> Article'


def test_highlighting_with_advanced_search(client, app):
    app.data.insert(
        "items",
        [
            {
                "_id": "foo",
                "body_html": "Story that involves cheese and onions",
                "slugline": "That's the test slugline cheese",
                "headline": "Demo Article",
            }
        ],
    )
    advanced_search_params = parse.quote('{"fields":[],"all":"demo"}')
    url = f"/wire/search?advanced={advanced_search_params}&es_highlight=1"
    resp = client.get(url)
    data = json.loads(resp.get_data())
    assert data["_items"][0]["es_highlight"]["headline"][0] == '<span class="es-highlight">Demo</span> Article'

    advanced_search_params = parse.quote('{"fields":[],"any":"cheese"}')
    url = f"/wire/search?advanced={advanced_search_params}&es_highlight=1"
    resp = client.get(url)
    data = json.loads(resp.get_data())
    assert (
        data["_items"][0]["es_highlight"]["slugline"][0]
        == 'That\'s the test slugline <span class="es-highlight">cheese</span>'
    )
    assert (
        data["_items"][0]["es_highlight"]["body_html"][0] == 'Story that involves <span class="es-highlight">'
        "cheese</span> and onions"
    )


def test_french_accents_search(client, app):
    app.data.insert("items", [{"_id": "foo", "body_html": "Story that involves élection"}])
    resp = client.get("/wire/search?q=election")
    assert 1 == len(resp.json["_items"])
    resp = client.get("/wire/search?q=electión")
    assert 1 == len(resp.json["_items"])
