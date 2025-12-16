from bson import ObjectId

from newsroom import UserRole
from newsroom.cards import CardsResourceService
from newsroom.types import CardResourceModel, DashboardCardType, SectionEnum
from newsroom.wire.views import get_home_data, get_items_by_card
from newsroom.tests.fixtures import PUBLIC_USER_ID

from tests.core.utils import create_entries_for, update_entries_for, find_one_by_id


async def test_personal_dashboard_data(client, app, company_products):
    user = await find_one_by_id("users", PUBLIC_USER_ID)
    assert user

    topics = [
        {"_id": ObjectId(), "label": "fooo", "query": "weather", "user": PUBLIC_USER_ID, "topic_type": "wire"},
    ]

    await create_entries_for("topics", topics)

    await update_entries_for(
        "users",
        PUBLIC_USER_ID,
        {
            "dashboards": [
                {"name": "test d", "type": "4x4", "topic_ids": [topic["_id"] for topic in topics]},
            ]
        },
        user,
    )

    async with app.test_request_context("/") as request:
        request.session["user"] = str(PUBLIC_USER_ID)
        data = await get_home_data()

    assert "personalizedDashboards" in data
    dashboard_data = data["personalizedDashboards"][0]
    assert dashboard_data["dashboard_name"] == "test d"
    assert dashboard_data["dashboard_id"] == "d0"
    topic_items = dashboard_data["topic_items"]
    assert 1 == len(topic_items)
    assert topic_items[0]["_id"] == topics[0]["_id"]
    assert 1 == len(topic_items[0]["items"])
    assert "Weather" == topic_items[0]["items"][0]["headline"]
    assert topic_items[0]["items"][0]["_access"]


async def test_dashboard_data(client, app, company_products):
    app.config["PERMISSION_DASHBOARD_CARDS"] = True
    user = await find_one_by_id("users", PUBLIC_USER_ID)
    assert user

    company_id = ObjectId()
    wire_product_id = ObjectId()
    wire_product_restrictive_id = ObjectId()
    card_id = ObjectId()

    await create_entries_for(
        "companies",
        [
            {
                "_id": company_id,
                "name": "Test Company",
                "is_enabled": True,
                "products": [
                    {"_id": wire_product_restrictive_id, "section": SectionEnum.WIRE.value},
                ],
                "sections": {"wire": True},
            }
        ],
    )
    await update_entries_for("users", user["_id"], {"company": company_id, "user_type": UserRole.PUBLIC.value}, user)

    await create_entries_for(
        "products",
        [
            {
                "_id": wire_product_id,
                "name": "Test Wire Product",
                "is_enabled": True,
                "product_type": SectionEnum.WIRE,
                "query": "*",
            },
            {
                "_id": wire_product_restrictive_id,
                "name": "Test Wire restrictive Product",
                "is_enabled": True,
                "product_type": SectionEnum.WIRE,
                "query": "headline:Amazon",
            },
        ],
    )

    card = await CardsResourceService().create(
        [
            CardResourceModel(
                id=card_id,
                label="News",
                dashboard_type=DashboardCardType.PIC_TEXT_4,
                dashboard="newsroom",
                config=dict(
                    product=str(wire_product_id),
                    size=6,
                ),
            )
        ]
    )

    async with app.test_request_context("/card_items") as request:
        request.session["user"] = str(PUBLIC_USER_ID)
        data = await get_items_by_card(card, company_id)
        assert len(data.get("News")) == 3
        assert data.get("News")[0].get("_access")
        assert not data.get("News")[1].get("_access")
        assert not data.get("News")[2].get("_access")
