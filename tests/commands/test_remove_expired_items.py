from datetime import datetime, timedelta
from newsroom.commands.remove_expired import remove_expired
from newsroom.utils import find_one
from tests.core.utils import create_entries_for


async def test_remove_expired_items(app):
    items = [
        {"_id": "expired", "versioncreated": datetime(2020, 10, 1), "expiry": datetime.now() - timedelta(days=1)},
    ]

    await create_entries_for("items", items)

    await remove_expired(1)

    expired = find_one("items", _id="expired")
    assert expired is None
