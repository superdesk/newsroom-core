from datetime import datetime, timedelta
from newsroom.utils import query_resource
from content_api.commands import RemoveExpiredItems


def test_remove_expired_items(app):
    items = [
        {"_id": "expired", "_updated": datetime.utcnow(), "expiry": datetime.utcnow() - timedelta(days=1)},
        {
            "_id": "expired2",
            "_updated": datetime.utcnow() - timedelta(days=1),
            "expiry": datetime.utcnow() - timedelta(days=1),
        },
        {"_id": "expired3", "_updated": datetime.utcnow() - timedelta(days=800)},
        {"_id": "not-expired", "_updated": datetime.utcnow(), "expiry": datetime.utcnow() + timedelta(days=90)},
        {
            "_id": "not-expired2",
            "_updated": datetime.utcnow() - timedelta(800),
            "expiry": datetime.utcnow() + timedelta(days=1),
        },
    ]

    app.data.remove("items")
    app.data.insert("items", items)

    assert query_resource("items").count() == len(items)

    app.config.update({"CONTENT_API_EXPIRY_DAYS": 500})
    RemoveExpiredItems().run()

    cursor = query_resource("items")
    ids = [doc["_id"] for doc in cursor]
    assert 2 == cursor.count(), ids

    ids = [doc["_id"] for doc in cursor]
    assert "not-expired" in ids
    assert "not-expired2" in ids
