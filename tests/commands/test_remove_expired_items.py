from datetime import timedelta

from superdesk.utc import utcnow
from newsroom.wire import WireItemService
from newsroom.commands.remove_expired import remove_expired

from tests.core.utils import create_entries_for, delete_entries_for


async def test_remove_expired_items(app):
    now = utcnow()
    items = [
        {"_id": "expired", "_updated": now, "expiry": now - timedelta(days=1)},
        {"_id": "expired2", "_updated": now - timedelta(days=1), "expiry": now - timedelta(days=1)},
        {"_id": "expired3", "_updated": now - timedelta(days=800)},
        {"_id": "not-expired", "_updated": now, "expiry": now + timedelta(days=90)},
        {"_id": "not-expired2", "_updated": now - timedelta(800), "expiry": now + timedelta(days=1)},
    ]

    await delete_entries_for("items")
    await create_entries_for("items", items)

    service = WireItemService()
    assert await service.count(use_mongo=True) == len(items)

    app.config.update({"CONTENT_API_EXPIRY_DAYS": 500})
    await remove_expired(None)

    ids = [doc.id async for doc in service.get_all()]
    assert 2 == await service.count(use_mongo=True), ids

    assert "not-expired" in ids
    assert "not-expired2" in ids
