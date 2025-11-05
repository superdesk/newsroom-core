from bson import ObjectId

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
