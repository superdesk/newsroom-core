from unittest.mock import patch


def ids(items):
    return {item["_id"] for item in items}


async def test_evolved_from_order(client, app):
    app.data.remove("items")

    async def push_item(data):
        resp = await client.post("/push", json=data)
        assert resp.status_code == 200

    async def search():
        resp = await client.get("/wire/search")
        assert 200 == resp.status_code
        return (await resp.get_json())["_items"]

    with patch.dict(app.config, {"PUSH_FIX_UPDATES": True}):
        await push_item(
            {
                "type": "text",
                "guid": "item3",
                "evolvedfrom": "item2",
            }
        )

        await push_item(
            {
                "type": "text",
                "guid": "item5",
                "evolvedfrom": "item4",
            }
        )

        items = await search()
        assert 2 == len(items)
        assert "item3" in ids(items)
        assert "item5" in ids(items)

        await push_item({"type": "text", "guid": "item2", "evolvedfrom": "item1"})
        items = await search()
        assert 2 == len(items)
        assert "item3" in ids(items)
        assert "item5" in ids(items)

        await push_item({"type": "text", "guid": "item1"})
        items = await search()
        assert 2 == len(items)
        assert "item3" in ids(items)
        assert "item5" in ids(items)

        await push_item({"type": "text", "guid": "item4", "evolvedfrom": "item3"})
        items = await search()
        assert 1 == len(items)
        assert "item5" in ids(items)
        assert ["item1", "item2", "item3", "item4"] == items[0]["ancestors"]
        assert "item1" == items[0]["original_id"]
