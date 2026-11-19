import quart
import logging
from bson import ObjectId
from datetime import datetime, timedelta, timezone

from newsroom.topics.topics_async import TopicService
from newsroom.users import UsersService
from superdesk.utc import utcnow, utc_to_local
from newsroom.types import (
    NotificationQueue,
    NotificationTopic,
    UserResourceModel,
    TopicResourceModel,
    NotificationScheduleModel,
)
from newsroom.notifications import NotificationQueueService
from newsroom.notifications.commands import SendScheduledNotificationEmails
from tests.core.utils import create_entries_for, get_all


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
    topic = await TopicService().find_by_id(topic_id)

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
    item = await command.get_latest_item_from_topic_queue(
        topic_queue, topic, UserResourceModel.from_dict(user), None, set()
    )

    assert item["_id"] == "topic1_item1"
    from superdesk.core import json

    print(json.dumps(item))
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
    user_topics = {topic["_id"]: TopicResourceModel.from_dict(topic) for topic in await get_all("topics")}
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
    topic_entries, topic_match_table = await command.get_topic_entries_and_match_table(
        schedule, UserResourceModel.from_dict(user), None, user_topics
    )

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
    assert command.is_scheduled_to_run_for_user(NotificationScheduleModel(timezone=timezone), utcnow(), True) is True

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
        schedule = NotificationScheduleModel(
            timezone=timezone,
            times=times,
        )
        if test.get("last_run"):
            schedule.last_run_time = create_datetime_instance(test["last_run"][0], test["last_run"][1])

        now = create_datetime_instance(test["now"][0], test["now"][1])

        assert command.is_scheduled_to_run_for_user(schedule, now, False) == test["result"], test


async def test_scheduled_notification_run_logging(app, mocker, caplog):
    now = datetime(2026, 11, 17, 15, tzinfo=timezone.utc)
    users = await UsersService().create(
        [
            {
                "first_name": "Scheduled",
                "last_name": "User",
                "email": f"scheduled-{index}@example.com",
                "user_type": "administrator",
                "receive_email": receive_email,
                "is_enabled": is_enabled,
                "notification_schedule": {"timezone": "UTC", "times": [scheduled_time]},
            }
            for index, (receive_email, scheduled_time, is_enabled) in enumerate(
                [
                    (True, "15:00", True),
                    (False, "15:00", True),
                    (True, "16:00", True),
                    (True, "15:00", True),
                    (True, "15:00", False),
                ]
            )
        ]
    )
    topic = (
        await TopicService().create(
            [
                {
                    "label": "Cheesy Stuff",
                    "query": "cheese",
                    "topic_type": "wire",
                    "subscribers": [{"user_id": u.id, "notification_type": "scheduled"} for u in users],
                }
            ]
        )
    )[0]
    item = {
        "_id": "scheduled-cheese-item",
        "type": "text",
        "headline": "Demo cheese article",
        "body_html": "<p>A story about cheese.</p>",
        "versioncreated": now,
    }
    await create_entries_for("items", [item])
    service = NotificationQueueService()
    for user in users:
        await service.add_item_to_queue(user.id, "wire", topic.id, item)

    mocker.patch("newsroom.notifications.commands.utcnow", return_value=now)
    send = app.mail.send

    def send_with_failure(message):
        if message.recipients == [users[3].email]:
            raise RuntimeError("transport unavailable")
        return send(message)

    mocker.patch.object(app.mail, "send", side_effect=send_with_failure)
    command = SendScheduledNotificationEmails()
    with caplog.at_level(logging.DEBUG, logger="newsroom.notifications.commands"):
        with app.mail.record_messages() as outbox:
            await command.run()

    assert len(outbox) == 1
    assert outbox[0].recipients == [users[0].email]
    assert "Demo cheese article" in outbox[0].body
    remaining = await service.search({})
    assert {queue.user for queue in await remaining.to_list()} == {users[2].id, users[3].id}
    for index, user in enumerate(users):
        saved = await UsersService().find_by_id(user.id)
        assert saved is not None
        assert saved.notification_schedule is not None
        assert saved.notification_schedule.last_run_time == (now if index in (0, 1) else None)
    messages = [record.getMessage() for record in caplog.records if record.name == "newsroom.notifications.commands"]
    assert messages
    assert all(message.startswith(command.log_msg) for message in messages)
    assert "Email send call completed" in caplog.text
    assert "reason=email_disabled" in caplog.text
    assert "reason=email_skipped" in caplog.text
    assert "reason=schedule_not_due timezone=UTC" in caplog.text
    assert "times=['16:00'] last_run_time=None" in caplog.text
    assert "reason=user_missing_or_user_company_inactive_or_expired" in caplog.text
    assert f"Failed to run schedule for user={users[3].id}" in caplog.text
    assert "transport unavailable" in caplog.text
    assert "template=scheduled_notification_topic_matches_email queued_items=1 wire_entries=1" in caplog.text
    assert (
        "status=completed_with_errors queues_examined=5 users_due=3 send_completed=1 "
        "skipped_not_due=1 skipped_inactive_or_missing=1 skipped_email=1 failures=1 duration_seconds="
    ) in caplog.text
    assert all(user.email not in "\n".join(messages) for user in users)


async def test_scheduled_notification_data_failure_logging(mocker, caplog):
    mocker.patch.object(NotificationQueueService, "search", side_effect=RuntimeError("data unavailable"))

    with caplog.at_level(logging.INFO, logger="newsroom.notifications.commands"):
        await SendScheduledNotificationEmails().run()

    assert "Failed to retrieve data to run schedules" in caplog.text
    assert "data unavailable" in caplog.text
    assert "status=completed_with_errors queues_examined=0 users_due=0 send_completed=0" in caplog.text
    assert "failures=1" in caplog.text


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
