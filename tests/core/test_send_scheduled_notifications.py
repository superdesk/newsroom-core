import quart
from bson import ObjectId
from datetime import datetime, timedelta

from newsroom.topics.topics_async import TopicService
from superdesk.utc import utcnow, utc_to_local
from newsroom.types import NotificationSchedule
from newsroom.notifications import NotificationQueueService
from newsroom.notifications.commands import SendScheduledNotificationEmails

from newsroom.notifications.models import NotificationQueue, NotificationTopic

from tests.core.utils import create_entries_for


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


async def test_get_queue_entries_for_section(user):
    command = SendScheduledNotificationEmails()

    now_3hr = utcnow() - timedelta(hours=3)
    now_2hr = utcnow() - timedelta(hours=2)
    now_1hr = utcnow() - timedelta(hours=1)

    topics_ids = await create_entries_for(
        "topics",
        [
            {"_id": ObjectId(), "label": "test1", "topic_type": "wire"},
            {
                "_id": ObjectId(),
                "label": "test2",
                "topic_type": "wire",
            },
            {
                "_id": ObjectId(),
                "label": "test3",
                "topic_type": "wire",
            },
        ],
    )

    queue_data = {
        "user": user["_id"],
        "topics": [
            {
                "topic_id": topics_ids[0],
                "items": ["topic1_item1"],
                "section": "wire",
                "last_item_arrived": now_3hr,
            },
            {
                "topic_id": topics_ids[1],
                "items": ["topic2_item1"],
                "section": "agenda",
                "last_item_arrived": now_2hr,
            },
            {
                "topic_id": topics_ids[2],
                "items": ["topic3_item1", "topic3_item2"],
                "section": "wire",
                "last_item_arrived": now_1hr,
            },
        ],
    }

    ids = await create_entries_for("notification_queue", [queue_data])
    queue = await NotificationQueueService().find_by_id(ids[0])

    entries = command.get_queue_entries_for_section(queue, "wire")

    assert entries[0].items == ["topic3_item1", "topic3_item2"]
    assert entries[0].section == "wire"
    assert entries[0].last_item_arrived == now_1hr

    assert entries[1].items == ["topic1_item1"]
    assert entries[1].section == "wire"
    assert entries[1].last_item_arrived == now_3hr

    entries = command.get_queue_entries_for_section(queue, "agenda")
    assert len(entries) == 1
    assert entries[0].section == "agenda"


async def test_get_latest_item_from_topic_queue(app, user):
    topic_id = (
        await create_entries_for(
            "topics",
            [
                {
                    "label": "Cheesy Stuff",
                    "query": "cheese",
                    "topic_type": "wire",
                }
            ],
        )
    )[0]
    topic = (await TopicService().find_by_id(topic_id)).to_dict()

    await create_entries_for(
        "items",
        [
            {
                "_id": "topic1_item1",
                "body_html": "Story that involves cheese and onions",
                "slugline": "That's the test slugline cheese",
                "headline": "Demo Article",
                "versioncreated": utcnow(),
            }
        ],
    )

    topic_queue = NotificationTopic(
        topic_id=topic_id,
        items=["topic1_item1"],
        section="wire",
        last_item_arrived=utcnow(),
    )

    command = SendScheduledNotificationEmails()
    item = command.get_latest_item_from_topic_queue(topic_queue, topic, user, None, set())

    assert item["_id"] == "topic1_item1"
    assert '<span class="es-highlight">cheese</span>' in item["es_highlight"]["body_html"][0]
    assert '<span class="es-highlight">cheese</span>' in item["es_highlight"]["slugline"][0]


async def test_get_topic_entries_and_match_table(app, user):
    topics_ids = await create_entries_for(
        "topics",
        [
            {
                "_id": ObjectId(),
                "label": "Cheesy Stuff",
                "query": "cheese",
                "topic_type": "wire",
            },
            {
                "_id": ObjectId(),
                "label": "Onions",
                "query": "onions",
                "topic_type": "wire",
            },
        ],
    )
    user_topics = {topic["_id"]: topic for topic in app.data.find_all("topics")}
    await create_entries_for(
        "items",
        [
            {
                "_id": "topic1_item1",
                "body_html": "Story that involves cheese and onions",
                "slugline": "That's the test slugline cheese",
                "headline": "Demo Article",
                "versioncreated": utcnow(),
            }
        ],
    )

    schedule = NotificationQueue(
        id=ObjectId(),
        user=user["_id"],
        topics=[
            NotificationTopic(
                items=["topic1_item1"], topic_id=topics_ids[0], last_item_arrived=utcnow(), section="wire"
            ),
            NotificationTopic(
                items=["topic1_item1"], topic_id=topics_ids[1], last_item_arrived=utcnow(), section="wire"
            ),
        ],
    )

    command = SendScheduledNotificationEmails()
    topic_entries, topic_match_table = command.get_topic_entries_and_match_table(schedule, user, None, user_topics)

    assert len(topic_entries["wire"]) == 1
    assert topic_entries["wire"][0]["topic"]["label"] == "Cheesy Stuff"
    assert topic_entries["wire"][0]["item"]["_id"] == "topic1_item1"

    assert len(topic_match_table["wire"]) == 2
    assert topic_match_table["wire"][0] == ("Cheesy Stuff", 1)
    assert topic_match_table["wire"][1] == ("Onions", 1)


async def test_is_scheduled_to_run_for_user():
    command = SendScheduledNotificationEmails()
    timezone = "Australia/Sydney"

    # Run schedule if ``last_run_time`` is not defined and ``force=True``
    assert command.is_scheduled_to_run_for_user({"timezone": timezone}, utcnow(), True) is True

    times = ["07:00", "15:00", "20:00"]
    tests = [
        {"result": False, "now": (6, 59), "last_run": (1, 0)},
        {"result": True, "now": (7, 4), "last_run": (1, 0)},
        {"result": False, "now": (6, 0)},
        {"result": True, "now": (7, 0)},
        {"result": False, "now": (10, 0), "last_run": (7, 0)},
        {"result": True, "now": (15, 0), "last_run": (7, 0)},
        {"result": False, "now": (19, 45), "last_run": (15, 1)},
        {"result": True, "now": (20, 0), "last_run": (15, 1)},
        {"result": False, "now": (22, 0), "last_run": (20, 0)},
        {"result": False, "now": (2, 0), "last_run": (20, 0)},
    ]

    def create_datetime_instance(hour: int, minute: int) -> datetime:
        return utc_to_local(timezone, utcnow()).replace(hour=hour, minute=minute, second=0, microsecond=0)

    for test in tests:
        schedule: NotificationSchedule = {
            "timezone": timezone,
            "times": times,
        }
        if test.get("last_run"):
            schedule["last_run_time"] = create_datetime_instance(test["last_run"][0], test["last_run"][1])

        now = create_datetime_instance(test["now"][0], test["now"][1])

        assert command.is_scheduled_to_run_for_user(schedule, now, False) == test["result"], test


async def test_scheduled_notification_topic_matches_template():
    template = "scheduled_notification_topic_matches_email.txt"

    kwargs = {
        "topic_match_table": {
            "wire": [
                ("foo", 2),
                ("bar", 3),
            ],
            "agenda": [
                ("agenda topic", 5),
            ],
        },
        "entries": {
            "wire": [
                {
                    "topic": {"_id": "topic-id"},
                    "item": {"headline": "Test Article", "service": []},
                },
                {
                    "topic": {"_id": "topic-id"},
                    "item": {"headline": "Test Article 2", "service": [{"name": "Sports"}]},
                },
            ],
            "agenda": [
                {
                    "topic": {"_id": "topic-id"},
                    "item": {
                        "name": "Test Event",
                        "dates": {
                            "start": datetime(2023, 9, 22, 10, 0, 0),
                            "end": datetime(2023, 9, 22, 12, 0, 0),
                        },
                        "versioncreated": datetime(2023, 9, 20, 12, 0, 0),
                    },
                },
            ],
        },
    }

    output = await quart.render_template(template, **kwargs)
    assert output
    assert "Test Event" in output
    assert "Test Article" in output
    assert "Category: Sports" in output
