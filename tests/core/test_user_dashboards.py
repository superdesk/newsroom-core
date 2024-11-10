from bson import ObjectId
import tests.utils as utils

from newsroom.types import UserResourceModel, CompanyResource, TopicResourceModel
from newsroom.wire.views import get_personal_dashboards_data
from newsroom.users import UsersService
from newsroom.companies import CompanyServiceAsync
from newsroom.topics.topics_async import TopicService

from datetime import datetime
from tests.core.utils import create_entries_for, delete_entries_for, update_entries_for


async def test_user_dashboards(app, client, public_user, public_company, company_products):
    topics = [{"label": "test", "user": public_user["_id"], "query": "bar", "topic_type": "agenda"}]
    topic_id = (await create_entries_for("topics", topics))[0]
    topic = await TopicService().find_by_id(topic_id)

    await delete_entries_for("products")
    products = [{"name": "test", "query": "foo", "is_enabled": True, "product_type": "wire"}]
    await create_entries_for("products", products)

    await update_entries_for(
        "companies",
        public_company["_id"],
        {
            "products": [{"_id": p["_id"], "section": p["product_type"], "seats": 0} for p in products],
            "sections": {"wire": True},
        },
        public_company,
    )
    public_company_instance = await CompanyServiceAsync().find_by_id(public_company["_id"])
    assert 1 == len(public_company_instance.products)

    await create_entries_for(
        "items",
        [
            {"_id": "test1", "guid": "test1", "headline": "foo", "versioncreated": datetime.utcnow()},
            {"_id": "test2", "guid": "test2", "headline": "bar", "versioncreated": datetime.utcnow()},
            {"_id": "test3", "guid": "test3", "headline": "baz", "versioncreated": datetime.utcnow()},
            {"_id": "test4", "guid": "test4", "headline": "foo bar", "versioncreated": datetime.utcnow()},
        ],
    )

    await utils.login(client, public_user)

    await utils.patch_json(
        client,
        f"/api/_users/{public_user['_id']}",
        {
            "dashboards": [{"name": "test", "type": "test", "topic_ids": [topic_id]}],
        },
    )

    data = await utils.get_json(
        client,
        f"/api/_users/{public_user['_id']}",
    )

    assert data["dashboards"]

    # reload user with dashboards
    public_user_instance = await UsersService().find_by_id(public_user["_id"])

    dashboards = await get_personal_dashboards_data(public_user_instance, public_company_instance, [topic])
    assert 1 == len(dashboards)
    topic_items = dashboards[0]["topic_items"][0]["items"]
    assert 1 == len(topic_items)
    assert "test4" == topic_items[0]["guid"]

    await utils.delete_json(
        client,
        f"/topics/{topic_id}",
    )

    data = await utils.get_json(
        client,
        f"/api/_users/{public_user_instance.id}",
    )

    assert "dashboards" in data
    assert data["dashboards"][0]["topic_ids"] == []


async def test_dashboard_data_for_user_without_wire_section(app):
    products = [
        {"name": "Sports", "product_type": "wire"},
    ]

    await create_entries_for("products", products)

    topic = TopicResourceModel.from_dict(
        {
            "_id": ObjectId("65b968911298768bef93c53f"),
            "label": "Sonia Bélanger",
            "_created": None,
            "filter": {"language": []},
            "query": '"Sonia Bélanger"',
            "topic_type": "wire",
        }
    )

    company = CompanyResource.from_dict(
        {
            "_id": ObjectId(),
            "name": "Does",
            "products": [{"_id": products[0]["_id"], "section": "wire"}],
            "sections": {"wire": True},
        }
    )

    user = UserResourceModel.from_dict(
        {
            "id": ObjectId(),
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@company.org",
            "user_type": "company_admin",
            "company": company.id,
            "sections": {"wire": False},
            "dashboards": [{"type": "4-picture-text", "topic_ids": [topic.id], "name": "My Home"}],
        }
    )

    data = await get_personal_dashboards_data(user, company, [topic])
    assert data
