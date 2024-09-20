import bson

# import tests.utils as utils

from newsroom.wire.views import get_personal_dashboards_data

# from datetime import datetime
# from tests.core.utils import create_entries_for

# TODO-ASYNC ;- Need to check why api/_users/<users_id> is not working got 404p

# async def test_user_dashboards(app, client, public_user, public_company, company_products):
#     topics = [
#         {
#             "_id": bson.ObjectId('59b4c5c61d41c8d736852fb3'),
#             "label": "test",
#             "user": public_user["_id"],
#             "query": "bar",
#             "company": public_user["company"],
#             "topic_type": "wire",
#         }
#     ]
#     create_entries_for("topics", topics)

#     app.data.remove("products")
#     products = [{"name": "test", "query": "foo", "is_enabled": True, "product_type": "wire"}]
#     app.data.insert("products", products)

#     assert app.data.update(
#         "companies",
#         public_company["_id"],
#         {
#             "products": [{"_id": p["_id"], "section": p["product_type"], "seats": 0} for p in products],
#             "sections": {"wire": True},
#         },
#         public_company,
#     )
#     public_company = app.data.find_one("companies", req=None, _id=public_company["_id"])
#     assert 1 == len(public_company["products"])

#     app.data.insert(
#         "items",
#         [
#             {"guid": "test1", "headline": "foo", "versioncreated": datetime.utcnow()},
#             {"guid": "test2", "headline": "bar", "versioncreated": datetime.utcnow()},
#             {"guid": "test3", "headline": "baz", "versioncreated": datetime.utcnow()},
#             {"guid": "test4", "headline": "foo bar", "versioncreated": datetime.utcnow()},
#         ],
#     )

#     await utils.login(client, public_user)

#     await utils.patch_json(
#         client,
#         f"/api/_users/{public_user['_id']}",
#         {
#             "dashboards": [{"name": "test", "type": "test", "topic_ids": [t["_id"] for t in topics]}],
#         },
#     )

#     data = await utils.get_json(
#         client,
#         f"/api/_users/{public_user['_id']}",
#     )

#     assert data["dashboards"]

#     # reload user with dashboards
#     public_user = app.data.find_one("users", req=None, _id=public_user["_id"])

#     dashboards = get_personal_dashboards_data(public_user, public_company, topics)
#     assert 1 == len(dashboards)
#     topic_items = dashboards[0]["topic_items"][0]["items"]
#     assert 1 == len(topic_items)
#     assert "test4" == topic_items[0]["guid"]

#     await utils.delete_json(
#         client,
#         f"/topics/{topics[0]['_id']}",
#     )

#     data = await utils.get_json(
#         client,
#         f"/api/_users/{public_user['_id']}",
#     )

#     assert "dashboards" in data
#     assert data["dashboards"][0]["topic_ids"] == []


async def test_dashboard_data_for_user_without_wire_section(app):
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
