from pytest import fixture
import pytz
from quart import json, g, session as server_session
from datetime import datetime, timedelta
from urllib import parse
from bson import ObjectId
from copy import deepcopy

from newsroom.companies import CompanyServiceAsync
from newsroom.wire.search import WireSearchService, SearchQuery

from tests.core.utils import add_company_products, create_entries_for
from ..fixtures import (  # noqa: F401
    items,
    init_items,
    init_auth,
    init_company,
    PUBLIC_USER_ID,
    PUBLIC_USER_EMAIL,
    COMPANY_1_ID,
    ADMIN_USER_EMAIL,
)
from ..utils import get_json, get_admin_user_id, login, mock_send_email
from unittest import mock
from newsroom.tests.users import ADMIN_USER_ID
from superdesk import get_resource_service


NAV_1 = ObjectId("5e65964bf5db68883df561c0")
NAV_2 = ObjectId("5e65964bf5db68883df561c1")

PROD_1 = ObjectId()
PROD_2 = ObjectId()


@fixture
async def setup_products(app):
    await create_entries_for(
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

    add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "_id": PROD_1,
                "name": "product test",
                "sd_product_id": 1,
                "navigations": [NAV_1],
                "product_type": "wire",
                "is_enabled": True,
            },
            {
                "_id": PROD_2,
                "name": "product test 2",
                "sd_product_id": 2,
                "navigations": [NAV_2],
                "product_type": "wire",
                "is_enabled": True,
            },
        ],
    )


async def test_item_detail(client):
    resp = await client.get("/wire/tag:foo")
    assert resp.status_code == 200
    html = (await resp.get_data()).decode("utf-8")
    assert "Amazon Is Opening More Bookstores" in html


async def test_item_json(client):
    resp = await client.get("/wire/tag:foo?format=json")
    data = json.loads(await resp.get_data())
    assert "headline" in data


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_share_items(client, app):
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
        resp = await client.post(
            "/wire_share",
            json={
                "items": [item["_id"] for item in items],
                "users": [str(user_ids[0])],
                "message": "Some info message",
            },
        )

        assert resp.status_code == 201, (await resp.get_data()).decode("utf-8")
        assert len(outbox) == 1
        assert outbox[0].recipients == ["foo2@bar.com"]
        assert outbox[0].sender == "newsroom@localhost"
        assert outbox[0].subject == "From Newshub: %s" % items[0]["headline"]
        assert "Hi Foo Bar" in outbox[0].body
        assert "admin admin (admin@sourcefabric.org) shared " in outbox[0].body
        assert items[0]["headline"] in outbox[0].body
        assert items[1]["headline"] in outbox[0].body
        assert "http://localhost:5050/wire?item=%s" % items[0]["_id"] in outbox[0].body
        assert "http://localhost:5050/wire?item=%s" % items[1]["_id"] in outbox[0].body
        # assert 'Some info message' in outbox[0].body

    resp = await client.get("/wire/{}?format=json".format(items[0]["_id"]))
    data = json.loads(await resp.get_data())
    assert "shares" in data

    user_id = get_admin_user_id(app)
    assert str(user_id) in data["shares"]


async def get_bookmarks_count(client, user):
    resp = await client.get("/api/wire_search?bookmarks=%s" % str(user))
    assert resp.status_code == 200
    data = json.loads(await resp.get_data())
    return data["_meta"]["total"]


async def test_bookmarks(client, app):
    user_id = get_admin_user_id(app)
    assert user_id

    assert 0 == await get_bookmarks_count(client, user_id)

    resp = await client.post("/wire_bookmark", json={"items": [items[0]["_id"]]})
    assert resp.status_code == 200

    assert 1 == await get_bookmarks_count(client, user_id)

    await client.delete("/wire_bookmark", json={"items": [items[0]["_id"]]})
    assert resp.status_code == 200

    assert 0 == await get_bookmarks_count(client, user_id)


async def test_bookmarks_by_section(client, app):
    add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "name": "Service A",
                "query": "service.code: a",
                "is_enabled": True,
                "description": "Service A",
                "sd_product_id": None,
                "product_type": "wire",
            },
        ],
    )

    await login(client, {"email": PUBLIC_USER_EMAIL})

    assert 0 == await get_bookmarks_count(client, PUBLIC_USER_ID)

    resp = await client.post("/wire_bookmark", json={"items": [items[0]["_id"]]})
    assert resp.status_code == 200

    assert 1 == await get_bookmarks_count(client, PUBLIC_USER_ID)

    await client.delete("/wire_bookmark", json={"items": [items[0]["_id"]]})
    assert resp.status_code == 200

    assert 0 == await get_bookmarks_count(client, PUBLIC_USER_ID)


async def test_item_copy(client, app):
    resp = await client.post("/wire/{}/copy".format(items[0]["_id"]))
    assert resp.status_code == 200

    resp = await client.get("/wire/tag:foo?format=json")
    data = json.loads(await resp.get_data())
    assert "copies" in data

    user_id = get_admin_user_id(app)
    assert str(user_id) in data["copies"]


async def test_versions(client, app):
    resp = await client.get("/wire/%s/versions" % items[0]["_id"])
    assert 200 == resp.status_code
    data = json.loads(await resp.get_data())
    assert len(data.get("_items")) == 0

    resp = await client.get("/wire/%s/versions" % items[1]["_id"])
    data = json.loads(await resp.get_data())
    assert 2 == len(data["_items"])
    assert "tag:weather" == data["_items"][0]["_id"]
    assert "AAP" == data["_items"][0]["source"]
    assert "c" == data["_items"][1]["service"][0]["code"]


async def test_search_filters_items_with_updates(client, app):
    resp = await client.get("/wire/search")
    data = json.loads(await resp.get_data())
    assert 3 == len(data["_items"])
    assert "tag:weather" not in [item["_id"] for item in data["_items"]]


async def test_search_includes_killed_items(client, app):
    app.data.insert(
        "items", [{"_id": "foo", "pubstatus": "canceled", "headline": "killed", "versioncreated": datetime.utcnow()}]
    )
    resp = await client.get("/wire/search?q=headline:killed")
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])


async def test_search_by_products_id(client, app):
    app.data.insert(
        "items",
        [
            {
                "_id": "foo",
                "headline": "product test",
                "products": [{"code": "12345"}],
                "versioncreated": datetime.utcnow(),
            }
        ],
    )
    resp = await client.get("/wire/search?q=products.code:12345")
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])


async def test_search_filter_by_category(client, app):
    resp = await client.get("/wire/search?filter=%s" % json.dumps({"service": ["Service A"]}))
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])


async def test_filter_by_product_anonymous_user_gets_all(client, app):
    resp = await client.get("/wire/search?products=%s" % json.dumps({"10": True}))
    data = json.loads(await resp.get_data())
    assert 3 == len(data["_items"])
    assert "_aggregations" in data


async def test_search_sort(client, app):
    resp = await client.get("/wire/search?sort=versioncreated:asc")
    data = json.loads(await resp.get_data())
    assert "urn:localhost:weather" == data["_items"][0]["_id"]

    resp = await client.get("/wire/search?sort=versioncreated:desc")
    data = json.loads(await resp.get_data())
    assert "urn:localhost:weather" == data["_items"][2]["_id"]

    resp = await client.get("/wire/search?q=weather+OR+flood+OR+waters&sort=_score")
    data = json.loads(await resp.get_data())
    assert "urn:localhost:flood" == data["_items"][0]["_id"]


async def test_logged_in_user_no_product_gets_no_results(client, app, public_user):
    await login(client, public_user)
    resp = await client.get("/wire/search")
    assert 403 == resp.status_code, await resp.get_data(as_text=True)
    resp = await client.get("/wire")
    assert 403 == resp.status_code
    assert "There is no product associated with your user." in await resp.get_data(as_text=True)


async def test_logged_in_user_no_company_gets_no_results(client, app, public_user):
    await login(client, public_user)
    resp = await client.get("/wire/search")
    assert resp.status_code == 403


async def test_administrator_gets_all_results(client, app):
    await login(client, {"email": ADMIN_USER_EMAIL})
    resp = await client.get("/wire/search")
    data = json.loads(await resp.get_data())
    assert 3 == len(data["_items"])


async def test_search_filtered_by_users_products(client, app, public_user):
    add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "name": "product test",
                "sd_product_id": 1,
                "is_enabled": True,
                "product_type": "wire",
            }
        ],
    )

    await login(client, public_user)
    resp = await client.get("/wire/search")
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])
    assert "_aggregations" in data


async def test_search_filter_by_individual_navigation(client, app, setup_products, public_user):
    await login(client, public_user)
    resp = await client.get("/wire/search")
    data = json.loads(await resp.get_data())
    assert 2 == len(data["_items"])
    assert "_aggregations" in data
    resp = await client.get(f"/wire/search?navigation={NAV_1}")
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])
    assert "_aggregations" in data

    # test admin user filtering
    await login(client, {"email": ADMIN_USER_EMAIL})
    resp = await client.get("/wire/search")
    data = json.loads(await resp.get_data())
    assert 3 == len(data["_items"])  # gets all by default

    resp = await client.get(f"/wire/search?navigation={NAV_1}")
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])


async def test_search_filtered_by_query_product(client, app, public_user):
    await create_entries_for(
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

    add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "name": "product test",
                "query": "headline:more",
                "navigations": [NAV_1],
                "product_type": "wire",
                "is_enabled": True,
            },
            {
                "name": "product test 2",
                "query": "headline:Weather",
                "navigations": [NAV_2],
                "product_type": "wire",
                "is_enabled": True,
            },
        ],
    )

    await login(client, public_user)
    resp = await client.get("/wire/search")
    data = json.loads(await resp.get_data())
    assert 2 == len(data["_items"])
    assert "_aggregations" in data
    resp = await client.get(f"/wire/search?navigation={NAV_2}")
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])
    assert "_aggregations" in data


async def test_search_pagination(client):
    resp = await client.get("/wire/search?from=25")
    assert 200 == resp.status_code
    data = json.loads(await resp.get_data())
    assert 0 == len(data["_items"])
    assert "_aggregations" not in data

    resp = await client.get("/wire/search?from=2000")
    assert 400 == resp.status_code


async def test_search_created_from(client):
    resp = await client.get("/wire/search?created_from=now/d")
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])

    resp = await client.get("/wire/search?created_from=now/w")
    data = json.loads(await resp.get_data())
    assert 1 <= len(data["_items"])

    resp = await client.get("/wire/search?created_from=now/M")
    data = json.loads(await resp.get_data())

    assert 1 <= len(data["_items"])


async def test_search_created_to(client):
    resp = await client.get("/wire/search?created_to=%s" % datetime.now().strftime("%Y-%m-%d"))
    data = json.loads(await resp.get_data())
    assert 3 == len(data["_items"])

    resp = await client.get(
        "/wire/search?created_to=%s&timezone_offset=%s"
        % ((datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"), -120)
    )
    data = json.loads(await resp.get_data())
    assert 0 == len(data["_items"])


async def test_item_detail_access(client, app, public_user):
    item_url = "/wire/%s" % items[0]["_id"]
    data = await get_json(client, item_url)
    assert data["_access"]
    assert data["body_html"]

    # public user
    await login(client, public_user)
    # no access by default
    data = await get_json(client, item_url)
    assert not data["_access"]
    assert not data.get("body_html")

    # add product
    add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "name": "matching product",
                "is_enabled": True,
                "product_type": "wire",
                "query": "slugline:%s" % items[0]["slugline"],
            }
        ],
    )

    # normal access
    data = await get_json(client, item_url)
    assert data["_access"]
    assert data["body_html"]


async def test_search_using_section_filter_for_public_user(client, app, public_user):
    await create_entries_for(
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

    add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "name": "product test",
                "query": "headline:more",
                "navigations": [NAV_1],
                "is_enabled": True,
                "product_type": "wire",
            },
            {
                "name": "product test 2",
                "query": "headline:Weather",
                "navigations": [NAV_2],
                "is_enabled": True,
                "product_type": "wire",
            },
        ],
    )

    g.pop("cached:navigations", None)

    await login(client, public_user)
    resp = await client.get("/wire/search")
    data = json.loads(await resp.get_data())
    assert 2 == len(data["_items"])
    assert "_aggregations" in data
    resp = await client.get(f"/wire/search?navigation={NAV_2}")
    data = json.loads(await resp.get_data())
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

    g.section_filters = None
    g.pop("cached:section_filters", None)

    resp = await client.get("/wire/search")
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])

    resp = await client.get(f"/wire/search?navigation={NAV_2}")
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])

    resp = await client.get(f"/wire/search?navigation={NAV_1}")
    data = json.loads(await resp.get_data())
    assert 0 == len(data["_items"])


async def test_administrator_gets_results_based_on_section_filter(client, app):
    await login(client, {"email": ADMIN_USER_EMAIL})
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

    resp = await client.get("/wire/search")
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])


async def test_time_limited_access(client, app, public_user):
    add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "name": "product test",
                "query": "versioncreated:<=now-2d",
                "is_enabled": True,
                "product_type": "wire",
            }
        ],
    )

    await login(client, public_user)

    resp = await client.get("/wire/search")
    data = json.loads(await resp.get_data())
    assert 2 == len(data["_items"])
    print(data["_items"][0]["versioncreated"])

    g.settings["wire_time_limit_days"]["value"] = 1
    resp = await client.get("/wire/search")
    data = json.loads(await resp.get_data())
    assert 0 == len(data["_items"])

    g.settings["wire_time_limit_days"]["value"] = 100
    resp = await client.get("/wire/search")
    data = json.loads(await resp.get_data())
    assert 2 == len(data["_items"])

    g.settings["wire_time_limit_days"]["value"] = 1
    company = app.data.find_one("companies", req=None, _id=COMPANY_1_ID)
    app.data.update("companies", COMPANY_1_ID, {"archive_access": True}, company)
    resp = await client.get("/wire/search")
    data = json.loads(await resp.get_data())
    assert 2 == len(data["_items"])


async def test_company_type_filter(client, app, public_user):
    add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "name": "product test",
                "query": "versioncreated:<=now-2d",
                "is_enabled": True,
                "product_type": "wire",
            }
        ],
    )

    await login(client, public_user)
    resp = await client.get("/wire/search")
    data = json.loads(await resp.get_data())
    assert 2 == len(data["_items"])

    app.config["COMPANY_TYPES"] = [
        dict(id="test", wire_must={"term": {"service.code": "b"}}),
    ]

    company = app.data.find_one("companies", req=None, _id=COMPANY_1_ID)
    app.data.update("companies", COMPANY_1_ID, {"company_type": "test"}, company)

    resp = await client.get("/wire/search")
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])
    assert "WEATHER" == data["_items"][0]["slugline"]

    app.config["COMPANY_TYPES"] = [
        dict(id="test", wire_must_not={"term": {"service.code": "b"}}),
    ]

    resp = await client.get("/wire/search")
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])
    assert "WEATHER" != data["_items"][0]["slugline"]


async def test_search_by_products_and_filtered_by_embargoe(app):
    async with app.test_request_context("/") as client:
        client.session["user"] = PUBLIC_USER_ID
        product_id = ObjectId()
        add_company_products(
            app,
            COMPANY_1_ID,
            [
                {
                    "_id": product_id,
                    "name": "product test",
                    "query": "headline:china",
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

        items = get_resource_service("wire_search").get_product_items(product_id, 20)
        assert 1 == len(items)

        app.config["COMPANY_TYPES"] = [
            dict(id="test", wire_must_not={"range": {"embargoed": {"gte": "now"}}}),
        ]

        await CompanyServiceAsync().update(COMPANY_1_ID, {"company_type": "test"})
        items = get_resource_service("wire_search").get_product_items(product_id, 20)
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

        items = get_resource_service("wire_search").get_product_items(product_id, 20)
        assert 1 == len(items)
        assert items[0]["headline"] == "china story"


async def test_wire_delete(client, app):
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

    resp = await client.delete("/wire", json={"items": [docs[0]["_id"]]})
    assert resp.status_code == 200

    for doc in docs:
        assert get_resource_service("items").find_one(req=None, _id=doc["_id"]) is None
        assert get_resource_service("items_versions").find_one(req=None, _id_document=doc["_id"]) is None


async def test_highlighting(client, app):
    app.data.insert(
        "items",
        [
            {
                "_id": "foo",
                "body_html": "Story that involves cheese and onions",
                "slugline": "That's the test slugline cheese",
                "headline": "Demo Article",
                "versioncreated": datetime.utcnow(),
            }
        ],
    )
    resp = await client.get("/wire/search?q=cheese&es_highlight=1")
    data = json.loads(await resp.get_data())
    assert (
        data["_items"][0]["es_highlight"]["body_html"][0] == 'Story that involves <span class="es-highlight">'
        "cheese</span> and onions"
    )
    assert (
        data["_items"][0]["es_highlight"]["slugline"][0]
        == 'That\'s the test slugline <span class="es-highlight">cheese</span>'
    )

    resp = await client.get("/wire/search?q=demo&es_highlight=1")
    data = json.loads(await resp.get_data())
    assert data["_items"][0]["es_highlight"]["headline"][0] == '<span class="es-highlight">Demo</span> Article'

    resp = await client.get(
        "/wire/search?q={query}&es_highlight=1".format(query='article AND "cheese and onions" AND "slugline" AND story')
    )
    data = json.loads(await resp.get_data())
    highlights = data["_items"][0]["es_highlight"]
    assert "slugline" in highlights
    assert "headline" in highlights
    assert "body_html" in highlights
    assert 4 == highlights["body_html"][0].count("es-highlight")


async def test_highlighting_with_advanced_search(client, app):
    app.data.insert(
        "items",
        [
            {
                "_id": "foo",
                "body_html": "Story that involves cheese and onions",
                "slugline": "That's the test slugline cheese",
                "headline": "Demo Article",
                "versioncreated": datetime.utcnow(),
            }
        ],
    )
    advanced_search_params = parse.quote('{"fields":[],"all":"demo"}')
    url = f"/wire/search?advanced={advanced_search_params}&es_highlight=1"
    resp = await client.get(url)
    data = json.loads(await resp.get_data())
    assert data["_items"][0]["es_highlight"]["headline"][0] == '<span class="es-highlight">Demo</span> Article'

    advanced_search_params = parse.quote('{"fields":[],"any":"cheese"}')
    url = f"/wire/search?advanced={advanced_search_params}&es_highlight=1"
    resp = await client.get(url)
    data = json.loads(await resp.get_data())
    assert (
        data["_items"][0]["es_highlight"]["slugline"][0]
        == 'That\'s the test slugline <span class="es-highlight">cheese</span>'
    )
    assert (
        data["_items"][0]["es_highlight"]["body_html"][0] == 'Story that involves <span class="es-highlight">'
        "cheese</span> and onions"
    )


async def test_french_accents_search(client, app):
    app.data.insert(
        "items", [{"_id": "foo", "body_html": "Story that involves élection", "versioncreated": datetime.utcnow()}]
    )
    resp = await client.get("/wire/search?q=election")
    assert 1 == len((await resp.get_json())["_items"])
    resp = await client.get("/wire/search?q=electión")
    assert 1 == len((await resp.get_json())["_items"])


async def test_navigation_for_public_users(client, app, setup_products):
    user = app.data.find_one("users", req=None, _id=PUBLIC_USER_ID)
    assert user

    company = app.data.find_one("companies", req=None, _id=COMPANY_1_ID)
    assert company

    # add products to user
    app.data.update(
        "users",
        PUBLIC_USER_ID,
        {"products": [{"section": "wire", "_id": PROD_1}, {"section": "wire", "_id": PROD_2}]},
        user,
    )

    # and remove those from company
    app.data.update(
        "companies",
        COMPANY_1_ID,
        {"products": [{"section": "wire", "_id": PROD_1, "seats": 1}, {"section": "wire", "_id": PROD_2, "seats": 1}]},
        company,
    )

    await login(client, user)

    # make sure user gets the products
    resp = await client.get("/wire/search")
    data = json.loads(await resp.get_data())
    assert 2 == len(data["_items"])

    # test navigation
    resp = await client.get(f"/wire/search?navigation={NAV_1}")
    data = json.loads(await resp.get_data())
    assert 1 == len(data["_items"])


async def test_date_filters(client, app):
    # remove all other's item
    app.data.remove("items")
    now = datetime.utcnow()
    app.config["DEFAULT_TIMEZONE"] = "Europe/Berlin"
    app.data.insert(
        "items",
        [
            {
                "_id": "tag:today",
                "type": "text",
                "versioncreated": now,
            },
            {
                "_id": "tag:Week",
                "type": "text",
                "version": 1,
                "versioncreated": now - timedelta(days=3),
            },
            {
                "_id": "tag:Week2",
                "type": "text",
                "version": 1,
                "versioncreated": now - timedelta(days=7),
            },
            {
                "_id": "tag:Week2_MOnday",
                "type": "text",
                "version": 1,
                "versioncreated": now - timedelta(days=11),
            },
            {
                "_id": "tag:Week2_SUNday",
                "type": "text",
                "version": 1,
                "versioncreated": now - timedelta(days=4),
            },
            {
                "_id": "tag:thisMonth",
                "type": "text",
                "version": 1,
                "versioncreated": now - timedelta(days=15),
            },
            {
                "_id": "tag:thisMonth2",
                "type": "text",
                "version": 1,
                "versioncreated": now - timedelta(days=30),
            },
            {
                "_id": "tag:lastMonth",
                "type": "text",
                "version": 1,
                "versioncreated": now - timedelta(days=40),
            },
            {
                "_id": "tag:twoMonthsAgo",
                "type": "text",
                "version": 1,
                "versioncreated": now - timedelta(days=60),
            },
        ],
    )

    # Default Last 7 days
    resp = await client.get("/wire/search")
    assert resp.status_code == 200
    json_data = await resp.get_json()
    assert len(json_data["_items"]) == 7
    assert json_data["_items"][0]["_id"] == "tag:today"
    assert json_data["_items"][1]["_id"] == "tag:Week"
    assert json_data["_items"][2]["_id"] == "tag:Week2_SUNday"
    assert json_data["_items"][3]["_id"] == "tag:Week2"
    assert json_data["_items"][4]["_id"] == "tag:Week2_MOnday"
    assert json_data["_items"][5]["_id"] == "tag:thisMonth"
    assert json_data["_items"][6]["_id"] == "tag:thisMonth2"

    # Test "Today" filter
    resp = await client.get("/wire/search?date_filter=today")
    assert resp.status_code == 200
    json_data = await resp.get_json()
    assert len(json_data["_items"]) == 1
    assert json_data["_items"][0]["_id"] == "tag:today"

    # Test "Last 7 days" filter
    resp = await client.get("/wire/search?date_filter=last_week")
    assert resp.status_code == 200

    # Test "Last 30 days" filter
    resp = await client.get("/wire/search?date_filter=last_30_days")
    assert resp.status_code == 200
    assert len((await resp.get_json())["_items"]) == 7

    # custom filter
    created_to = (now - timedelta(days=35)).strftime("%Y-%m-%d")
    created_from = (now - timedelta(days=70)).strftime("%Y-%m-%d")
    resp = await client.get(
        "/wire/search?date_filter=custom_date&created_from={}&created_to={}".format(created_from, created_to)
    )
    assert resp.status_code == 200
    json_data = await resp.get_json()
    assert len(json_data["_items"]) == 2
    assert json_data["_items"][0]["_id"] == "tag:lastMonth"
    assert json_data["_items"][1]["_id"] == "tag:twoMonthsAgo"


async def test_date_filters_query(client, app):
    service = WireSearchService()
    app.config["DEFAULT_TIMEZONE"] = "Europe/Berlin"

    async with app.test_request_context("/"):

        def _set_search_query(user_id, args):
            server_session["user"] = user_id
            search = SearchQuery()
            search.args = args
            service.apply_request_filter(search)
            return search.query["bool"]["must"]

        # Last week
        assert [
            {"range": {"versioncreated": {"gte": "now-1w/w", "lt": "now/w", "time_zone": "Europe/Berlin"}}}
        ] == _set_search_query(ADMIN_USER_ID, {"date_filter": "last_week"})

        # Last 30 Days
        assert [{"range": {"versioncreated": {"gte": "now-30d/d", "time_zone": "Europe/Berlin"}}}] == _set_search_query(
            ADMIN_USER_ID, {"date_filter": "last_30_days"}
        )

        # Today
        assert [{"range": {"versioncreated": {"gte": "now/d", "time_zone": "Europe/Berlin"}}}] == _set_search_query(
            ADMIN_USER_ID, {"date_filter": "today"}
        )

        # Default
        assert [{"range": {"versioncreated": {"gte": "now-30d/d", "time_zone": "Europe/Berlin"}}}] == _set_search_query(
            ADMIN_USER_ID, {}
        )

        # Custom Date
        assert [
            {
                "range": {
                    "versioncreated": {
                        "gte": datetime(2024, 6, 20, 0, 0, tzinfo=pytz.UTC),
                        "lte": datetime(2024, 6, 23, 23, 59, 59, tzinfo=pytz.UTC),
                    }
                }
            }
        ] == _set_search_query(
            ADMIN_USER_ID, {"date_filter": "custom_date", "created_from": "2024-06-20", "created_to": "2024-06-23"}
        )


async def test_bookmark_old_items(client, public_user, company_products):
    await login(client, public_user)
    resp = await client.get("/wire/search")
    assert 200 == resp.status_code
    assert len((await resp.get_json())["_items"])

    resp = await client.post("/wire_bookmark", json={"items": ["tag:foo", "tag:out-of-default-range"]})
    assert 200 == resp.status_code

    resp = await client.get("/wire/search?bookmarks={}".format(public_user["_id"]))
    assert resp.status_code == 200
    assert 2 == len((await resp.get_json())["_items"])
