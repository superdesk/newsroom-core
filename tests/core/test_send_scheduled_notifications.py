from datetime import timedelta
from bson import ObjectId

from superdesk.utc import utcnow, utc_to_local
from newsroom.types import Topic, NotificationQueueTopic
from newsroom.notifications.send_scheduled_notifications import SendScheduledNotificationEmails

from newsroom.tests.users import ADMIN_USER_ID


def test_convert_schedule_times():
    command = SendScheduledNotificationEmails()
    now_utc = utcnow()
    timezone = "Australia/Sydney"

    schedule_time_strings = ["08:00", "16:30", "20:15"]
    now_local = utc_to_local(timezone, now_utc)

    schedule_times = command._convert_schedule_times(now_local, schedule_time_strings)

    assert schedule_times[0].hour == 8
    assert schedule_times[0].minute == 0

    assert schedule_times[1].hour == 16
    assert schedule_times[1].minute == 30

    assert schedule_times[2].hour == 20
    assert schedule_times[2].minute == 15


def test_get_queue_entries_for_section():
    command = SendScheduledNotificationEmails()

    topic1_id = ObjectId("54d9a786f87bc2ff88d04021")
    topic2_id = ObjectId("54d9a786f87bc2ff88d04022")
    topic3_id = ObjectId("54d9a786f87bc2ff88d04023")
    now_3hr = utcnow() - timedelta(hours=3)
    now_2hr = utcnow() - timedelta(hours=2)
    now_1hr = utcnow() - timedelta(hours=1)

    queue = {
        "user": ObjectId(),
        "topics": [
            {
                "topic_id": topic1_id,
                "items": ["topic1_item1"],
                "section": "wire",
                "last_item_arrived": now_3hr,
            },
            {
                "topic_id": topic2_id,
                "items": ["topic2_item1"],
                "section": "agenda",
                "last_item_arrived": now_2hr,
            },
            {
                "topic_id": topic3_id,
                "items": ["topic3_item1", "topic3_item2"],
                "section": "wire",
                "last_item_arrived": now_1hr,
            },
        ],
    }

    entries = command._get_queue_entries_for_section(queue, "wire")
    assert entries == [
        {
            "topic_id": topic3_id,
            "items": ["topic3_item1", "topic3_item2"],
            "section": "wire",
            "last_item_arrived": now_1hr,
        },
        {
            "topic_id": topic1_id,
            "items": ["topic1_item1"],
            "section": "wire",
            "last_item_arrived": now_3hr,
        },
    ]

    entries = command._get_queue_entries_for_section(queue, "agenda")
    assert entries == [
        {
            "topic_id": topic2_id,
            "items": ["topic2_item1"],
            "section": "agenda",
            "last_item_arrived": now_2hr,
        }
    ]


def test_get_latest_item_from_topic_queue(app):
    user = app.data.find_one("users", req=None, _id=ADMIN_USER_ID)
    topic_id = app.data.insert(
        "topics",
        [
            {
                "label": "Cheesy Stuff",
                "query": "cheese",
                "topic_type": "wire",
            }
        ],
    )[0]
    topic: Topic = app.data.find_one("topics", req=None, _id=topic_id)
    app.data.insert(
        "items",
        [
            {
                "_id": "topic1_item1",
                "body_html": "Story that involves cheese and onions",
                "slugline": "That's the test slugline cheese",
                "headline": "Demo Article",
            }
        ],
    )

    topic_queue: NotificationQueueTopic = {
        "topic_id": topic_id,
        "items": ["topic1_item1"],
        "section": "wire",
        "last_item_arrived": utcnow(),
    }

    command = SendScheduledNotificationEmails()
    item = command._get_latest_item_from_topic_queue(topic_queue, topic, user, None)

    assert item["_id"] == "topic1_item1"
    assert '<span class="es-highlight">cheese</span>' in item["es_highlight"]["body_html"][0]
    assert '<span class="es-highlight">cheese</span>' in item["es_highlight"]["slugline"][0]
