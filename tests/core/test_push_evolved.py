from flask import json
from unittest.mock import patch


def ids(items):
    return {item["_id"] for item in items}


def test_evolved_from_order(client, app):
    app.data.remove("items")

    def push_item(data):
        resp = client.post("/push", data=json.dumps(data), content_type="application/json")
        assert resp.status_code == 200

    def search():
        resp = client.get("/wire/search")
        assert 200 == resp.status_code
        return resp.json["_items"]

    with patch.dict(app.config, {"PUSH_FIX_UPDATES": True}):
        push_item(
            {
                "type": "text",
                "guid": "item3",
                "evolvedfrom": "item2",
            }
        )

        push_item(
            {
                "type": "text",
                "guid": "item5",
                "evolvedfrom": "item4",
            }
        )

        items = search()
        assert 2 == len(items)
        assert "item3" in ids(items)
        assert "item5" in ids(items)

        push_item({"type": "text", "guid": "item2", "evolvedfrom": "item1"})
        items = search()
        assert 2 == len(items)
        assert "item3" in ids(items)
        assert "item5" in ids(items)

        push_item({"type": "text", "guid": "item1"})
        items = search()
        assert 2 == len(items)
        assert "item3" in ids(items)
        assert "item5" in ids(items)

        push_item({"type": "text", "guid": "item4", "evolvedfrom": "item3"})
        items = search()
        assert 1 == len(items)
        assert "item5" in ids(items)
        assert ["item1", "item2", "item3", "item4"] == items[0]["ancestors"]
        assert "item1" == items[0]["original_id"]
