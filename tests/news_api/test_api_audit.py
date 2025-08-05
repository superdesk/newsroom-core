from bson import ObjectId
from pytest import fixture

from newsroom.types import SectionEnum, NewsApiAuditResourceModel

from tests.core.utils import create_entries_for, find_one_for

company_id = "5c3eb6975f627db90c84093c"


async def audit_check(item_id):
    cursor = await NewsApiAuditResourceModel.get_service().search({})
    assert await cursor.count() == 1
    assert (await cursor.next()).items_id == [item_id]


@fixture(autouse=True)
async def init(app):
    product_ids = await create_entries_for(
        "products",
        [
            {
                "_id": ObjectId("5ab03a87bdd78169bb6d0783"),
                "name": "Sample Product X",
                "description": "a description",
                "navigations": ["5aa5e94ebdd7810884f66ed3"],
                "sd_product_id": None,
                "product_type": "news_api",
                "query": "fish",
                "is_enabled": True,
            }
        ],
    )
    await create_entries_for(
        "companies",
        [
            {
                "_id": ObjectId(company_id),
                "name": "Test Company",
                "is_enabled": True,
                "products": [
                    {
                        "_id": product_ids[0],
                        "section": SectionEnum.NEWS_API,
                    }
                ],
            }
        ],
    )


async def test_get_item_audit_creation(client, app):
    await create_entries_for(
        "items",
        [{"_id": "111", "pubstatus": "usable", "headline": "Headline of the story"}],
    )
    token = await _create_company_auth_token(company_id)
    response = await client.get(
        "api/v1/news/item/111?format=NINJSFormatter",
        headers={"Authorization": token.get("token")},
    )
    assert response.status_code == 200
    await audit_check("111")


async def test_get_all_company_products_audit_creation(client, app):
    token = await _create_company_auth_token(company_id)
    response = await client.get(
        "api/v1/account/products",
        headers={"Authorization": token.get("token")},
    )
    assert response.status_code == 200
    data = await response.get_json()
    assert len(data["_items"]) == 1
    await audit_check("5ab03a87bdd78169bb6d0783")


async def test_get_single_product_audit_creation(client, app):
    token = await _create_company_auth_token(company_id)
    response = await client.get(
        "api/v1/account/products/5ab03a87bdd78169bb6d0783",
        headers={"Authorization": token.get("token")},
    )
    assert response.status_code == 200
    data = await response.get_json()
    assert data["_id"] == "5ab03a87bdd78169bb6d0783"
    await audit_check("5ab03a87bdd78169bb6d0783")


async def test_search_audit_creation(client, app):
    await create_entries_for(
        "items",
        [
            {
                "_id": "5ab03a87bdd78169bb6d0785",
                "body_html": "Once upon a time there was a fish who could swim",
            },
            {
                "_id": "5ab03a87bdd78169bb6d0786",
                "body_html": "Once upon a time there was a aardvark that could not swim",
            },
        ],
    )

    token = await _create_company_auth_token(company_id)

    response = await client.get("/api/v1/news/search", headers={"Authorization": f"Token {token.get('token')}"})
    json_data = await response.get_json()

    assert len(json_data["_items"]) == 1
    await audit_check("5ab03a87bdd78169bb6d0785")


async def _create_company_auth_token(company_id):
    await create_entries_for("news_api_tokens", [{"company": ObjectId(company_id), "enabled": True}])
    return await find_one_for("news_api_tokens", company=ObjectId(company_id))
