from bson import ObjectId
from newsroom.types import SectionEnum
from tests.core.utils import create_entries_for, find_one_for


async def test_news_api_root_links(client, app):
    company_id = ObjectId()
    await create_entries_for(
        "companies",
        [{"_id": company_id, "name": "Test Company", "is_enabled": True}],
    )
    await create_entries_for("news_api_tokens", [{"company": company_id, "enabled": True}])
    token = await find_one_for("news_api_tokens", company=company_id)

    response = await client.get("/api/v1", headers={"Authorization": token.get("token")})
    assert response.status_code == 200
    data = await response.get_json()
    assert {child["href"]: child["title"] for child in data["_links"]["child"]} == {
        "assets/<path:asset_id>/<item_id>": "Download Asset (with Wire ID)",
        "assets/<string:asset_id>": "Download Asset",
        "atom/<path:token>": "ATOM Feed (URL auth)",
        "atom": "ATOM Feed (Header auth)",
        "rss/<path:token>": "RSS Feed (URL auth)",
        "rss": "RSS Feed (Header auth)",
        "news/search": "News Feed",
        "news/feed": "News Search",
        "news/item/<path:item_id>": "Get News Item",
        "account/products": "Account Products Search",
        "account/products/<string:product_id>": "Get Account Product",
    }


async def test_product_search(client, app):
    company_id = ObjectId()
    api_product_id = ObjectId()
    wire_product_id = ObjectId()
    await create_entries_for(
        "companies",
        [
            {
                "_id": company_id,
                "name": "Test Company",
                "is_enabled": True,
                "products": [
                    {"_id": api_product_id, "section": SectionEnum.NEWS_API},
                    {"_id": wire_product_id, "section": SectionEnum.WIRE.value},
                ],
                "sections": {"news_api": True, "wire": True},
            }
        ],
    )
    await create_entries_for(
        "products",
        [
            {
                "_id": api_product_id,
                "name": "Test API Product",
                "is_enabled": True,
                "product_type": SectionEnum.NEWS_API,
                "query": "*",
            },
            {
                "_id": wire_product_id,
                "name": "Test Wire Product",
                "is_enabled": True,
                "product_type": SectionEnum.WIRE,
                "query": "*",
            },
        ],
    )
    await create_entries_for("news_api_tokens", [{"company": company_id, "enabled": True}])
    token = await find_one_for("news_api_tokens", company=company_id)

    # Ask for all products ensure we only get one, the api one!
    response = await client.get("/api/v1/account/products", headers={"Authorization": token.get("token")})
    assert response.status_code == 200
    data = await response.get_json()
    assert data["_items"][0].get("_id") == str(api_product_id)
    assert data["_items"][0].get("name") == "Test API Product"
    assert len(data["_items"]) == 1

    # Request the details of that product to ensure we get the feed and the search endpoint references
    response = await client.get(
        f"/api/v1/account/products/{api_product_id}", headers={"Authorization": token.get("token")}
    )
    assert response.status_code == 200
    data = await response.get_json()
    assert data.get("_links").get("search").get("href") == f"news/search/?products={api_product_id}"
    assert data.get("_links").get("feed").get("href") == f"news/feed/?products={api_product_id}"
    response = await client.get(
        f"/api/v1/news/search/?products={api_product_id}", headers={"Authorization": token.get("token")}
    )
    assert response.status_code == 200

    # Ensure you can't jus make up a product
    bad_product = ObjectId()
    response = await client.get(
        f"/api/v1/news/search/?products={bad_product}", headers={"Authorization": token.get("token")}
    )
    assert response.status_code == 400

    # Ensure an error is returned for none API products
    response = await client.get(
        f"/api/v1/news/search/?products={wire_product_id}", headers={"Authorization": token.get("token")}
    )
    assert response.status_code == 400
