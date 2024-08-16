from datetime import datetime, timedelta
from newsroom.commands.remove_expired import remove_expired
from newsroom.utils import find_one


async def test_remove_expired_items(runner, app):
    items = [
        {"_id": "expired", "versioncreated": datetime(2020, 10, 1), "expiry": datetime.utcnow() - timedelta(days=1)},
    ]

    app.data.insert("items", items)

    async with app.app_context():
        remove_expired(1)

    expired = find_one("items", _id="expired")
    assert expired is None
