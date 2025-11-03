import pytest
import asyncio

from superdesk.utc import utcnow
from newsroom.wire import WireItemService
from newsroom.commands.elastic_reindex import elastic_reindex_handler

from tests.core.utils import create_entries_for, delete_entries_for


async def test_invalid_resource_raises_error():
    """Test that handler raises ValueError for invalid resource"""

    with pytest.raises(ValueError) as exc_info:
        await elastic_reindex_handler("invalid_resource", 1000)

    assert "Invalid resource 'invalid_resource'" in str(exc_info.value)
    assert "Must be one of: items, agenda, history" in str(exc_info.value)


async def test_empty_resource_raises_error():
    """Test that handler raises ValueError for empty resource"""

    with pytest.raises(ValueError) as exc_info:
        await elastic_reindex_handler("", 1000)

    assert "Invalid resource ''" in str(exc_info.value)


async def test_reindex_items_preserves_data():
    """Test that reindex successfully copies data from old ES index to new ES index"""

    test_items = [
        {
            "_id": "reindex-item-1",
            "headline": "Test Reindex Item 1",
            "versioncreated": utcnow(),
            "type": "text",
        },
        {
            "_id": "reindex-item-2",
            "headline": "Test Reindex Item 2",
            "versioncreated": utcnow(),
            "type": "text",
        },
        {
            "_id": "reindex-item-3",
            "headline": "Test Reindex Item 3",
            "versioncreated": utcnow(),
            "type": "text",
        },
    ]
    await delete_entries_for("items")
    await create_entries_for("items", test_items)

    service = WireItemService()
    cursor = await service.search({})
    elastic_count = await cursor.count()
    assert elastic_count == 3, f"ElasticSearch should have 3 items before reindex, found {elastic_count}"

    elastic_reindex_handler("items")
    await asyncio.sleep(2)  # Give ES time to complete the reindex operation

    cursor = await service.search({})
    elastic_count = await cursor.count()
    assert elastic_count == 3, f"ElasticSearch should have 3 items after reindex, found {elastic_count}"

    elastic_results = await cursor.to_list_raw()
    found_ids = {item["_id"] for item in elastic_results}
    expected_ids = {"reindex-item-1", "reindex-item-2", "reindex-item-3"}
    assert found_ids == expected_ids, f"Expected {expected_ids}, got {found_ids}"
