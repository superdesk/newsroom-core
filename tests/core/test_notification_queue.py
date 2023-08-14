import time
from bson import ObjectId

from superdesk import get_resource_service
from superdesk.utc import utcnow

from tests.fixtures import PUBLIC_USER_ID


def test_adding_and_clearing_notification_queue():
    service = get_resource_service("notification_queue")

    # Make sure the item doesn't already exist
    assert service.find_one(req=None, user=PUBLIC_USER_ID) is None

    now = utcnow()
    topic_id = ObjectId("54d9a786f87bc2ff88d04028")
    item1_id = ObjectId("64d9a786f87bc2ff88d04028")
    item = {
        "_id": item1_id,
        "versioncreated": now,
    }

    service.add_item_to_queue(PUBLIC_USER_ID, "wire", topic_id, item)
    queue = service.find_one(req=None, user=PUBLIC_USER_ID)

    assert queue is not None
    # assert queue.get("last_run_time") is None
    assert len(queue["topics"]) == 1
    assert queue["topics"][0]["topic_id"] == topic_id
    assert queue["topics"][0]["section"] == "wire"
    assert queue["topics"][0]["last_item_arrived"] == now
    assert queue["topics"][0]["items"] == [item1_id]

    now2 = utcnow()
    item2_id = ObjectId("64d9a786f87bc2ff88d04029")
    item = {
        "_id": item2_id,
        "versioncreated": now2,
    }
    service.add_item_to_queue(PUBLIC_USER_ID, "wire", topic_id, item)
    queue = service.find_one(req=None, user=PUBLIC_USER_ID)

    assert len(queue["topics"]) == 1
    assert queue["topics"][0]["last_item_arrived"] == now2
    assert queue["topics"][0]["items"] == [item1_id, item2_id]

    time.sleep(1)
    service.reset_queue(PUBLIC_USER_ID)
    queue = service.find_one(req=None, user=PUBLIC_USER_ID)
    assert len(queue["topics"]) == 0
    # assert queue["last_run_time"] > now2
