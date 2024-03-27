import bson
import tests.utils as utils

from newsroom.wire.views import get_personal_dashboards_data


def test_user_dashboards(app, client, public_user, public_company, company_products):
    topics = [{"label": "test", "user": public_user["_id"], "query": "bar"}]
    app.data.insert("topics", topics)

    app.data.remove("products")
    products = [{"name": "test", "query": "foo", "is_enabled": True, "product_type": "wire"}]
    app.data.insert("products", products)

    assert app.data.update(
        "companies",
        public_company["_id"],
        {
            "products": [{"_id": p["_id"], "section": p["product_type"], "seats": 0} for p in products],
            "sections": {"wire": True},
        },
        public_company,
    )
    public_company = app.data.find_one("companies", req=None, _id=public_company["_id"])
    assert 1 == len(public_company["products"])

    app.data.insert(
        "items",
        [
            {"guid": "test1", "headline": "foo"},
            {"guid": "test2", "headline": "bar"},
            {"guid": "test3", "headline": "baz"},
            {"guid": "test4", "headline": "foo bar"},
        ],
    )

    utils.login(client, public_user)

    utils.patch_json(
        client,
        f"/api/_users/{public_user['_id']}",
        {
            "dashboards": [{"name": "test", "type": "test", "topic_ids": [t["_id"] for t in topics]}],
        },
    )

    data = utils.get_json(
        client,
        f"/api/_users/{public_user['_id']}",
    )

    assert data["dashboards"]

    # reload user with dashboards
    public_user = app.data.find_one("users", req=None, _id=public_user["_id"])

    dashboards = get_personal_dashboards_data(public_user, public_company, topics)
    assert 1 == len(dashboards)
    topic_items = dashboards[0]["topic_items"][0]["items"]
    assert 1 == len(topic_items)
    assert "test4" == topic_items[0]["guid"]

    utils.delete_json(
        client,
        f"/topics/{topics[0]['_id']}",
    )

    data = utils.get_json(
        client,
        f"/api/_users/{public_user['_id']}",
    )

    assert "dashboards" in data
    assert data["dashboards"][0]["topic_ids"] == []


def test_dashboard_data_for_user_without_wire_section(app):
    products = [
        {"product_type": "wire"},
    ]

    app.data.insert("products", products)

    topic = {
        "_id": bson.ObjectId("65b968911298768bef93c53f"),
        "advanced": None,
        "created": None,
        "filter": {
            "language": [
                "fr",
            ],
        },
        "navigation": None,
        "query": '"Sonia Bélanger"',
        "topic_type": "wire",
    }

    user = {
        "user_type": "company_admin",
        "company": "foo",
        "sections": {
            "wire": False,
        },
        "dashboards": [{"type": "4-picture-text", "topic_ids": [topic["_id"]], "name": "My Home"}],
    }

    company = {
        "_id": "foo",
        "products": [
            {"_id": products[0]["_id"], "section": "wire"},
        ],
        "sections": {
            "wire": True,
        },
    }

    data = get_personal_dashboards_data(user, company, [topic])
    assert data
