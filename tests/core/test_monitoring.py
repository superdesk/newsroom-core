import os
from typing import List
from quart import json
from pytest import fixture
from bson import ObjectId

from tests.core.utils import create_entries_for, update_entries_for, find_one_by_id
from newsroom.monitoring.email_alerts import MonitoringEmailAlerts
from unittest import mock
from tests.utils import mock_send_email, post_json, login_public
from superdesk.utc import utcnow, utc_to_local, local_to_utc
from datetime import timedelta

from newsroom.monitoring import MonitoringProfileService


company_id = "5c3eb6975f627db90c84093c"
even_now = utcnow().replace(hour=4, minute=0)


def mock_utcnow():
    return utcnow().replace(minute=0)


def get_fixture_path(fixture):
    return os.path.join(os.path.dirname(__file__), "../fixtures", fixture)


@fixture(autouse=True)
async def init(app):
    await create_entries_for(
        "companies",
        [
            {
                "_id": ObjectId(company_id),
                "phone": "2132132134",
                "sd_subscriber_id": "12345",
                "name": "Press 2 Co.",
                "is_enabled": True,
                "contact_name": "Tom",
            }
        ],
    )

    await create_entries_for(
        "auth_user",
        [
            {
                "_id": ObjectId("5c53afa45f627d8333220f15"),
                "email": "foo_user@bar.com",
                "first_name": "Foo_First_name",
                "last_name": "Doe",
                "is_enabled": True,
                "receive_email": True,
                "company": ObjectId(company_id),
            },
            {
                "_id": ObjectId("5c4684645f627debec1dc3db"),
                "email": "foo_user2@bar.com",
                "first_name": "Foo_First_name2",
                "last_name": "Doe",
                "is_enabled": True,
                "receive_email": True,
            },
        ],
    )

    await create_entries_for(
        "monitoring",
        [
            {
                "_id": ObjectId("5db11ec55f627d8aa0b545fb"),
                "is_enabled": True,
                "users": [
                    ObjectId("5c53afa45f627d8333220f15"),
                    ObjectId("5c4684645f627debec1dc3db"),
                ],
                "company": ObjectId(company_id),
                "subject": "Monitoring Subject",
                "name": "W1",
                "_etag": "f023a8db3cdbe31e63ac4b0e6864f5a86ef07253",
                "description": "D3",
                "alert_type": "full_text",
                "query": "headline: (product)",
                "format_type": "monitoring_pdf",
                "schedule": {"interval": "immediate"},
            }
        ],
    )


async def test_non_admin_actions_fail(client, app):
    await login_public(client)

    response = await client.post(
        "/monitoring/new",
        json={
            "is_enabled": True,
            "users": [
                ObjectId("5c53afa45f627d8333220f15"),
                ObjectId("5c4684645f627debec1dc3db"),
            ],
            "company": ObjectId("5c3eb6975f627db90c84093c"),
            "subject": "",
            "name": "W2",
            "_etag": "f023a8db3cdbe31e63ac4b0e6864f5a86ef07253",
            "description": "D3",
            "alert_type": "full_text",
            "query": "hgnhgnhg",
            "schedule": {"interval": "immediate"},
        },
    )
    assert response.status_code == 403

    response = await client.post(
        "/monitoring/5db11ec55f627d8aa0b545fb/users",
        json={"users": [ObjectId("5c53afa45f627d8333220f15")]},
    )
    assert response.status_code == 403

    response = await client.post(
        "/monitoring/5db11ec55f627d8aa0b545fb/schedule",
        json={"schedule": {"interval": "immediate"}},
    )
    assert response.status_code == 403

    response = await client.get("/monitoring/schedule_companies")
    assert response.status_code == 403

    response = await client.post(
        "/monitoring/5db11ec55f627d8aa0b545fb/users",
        json={"users": [ObjectId("5c53afa45f627d8333220f15")]},
    )
    assert response.status_code == 403


async def test_fetch_monitoring(client):
    response = await client.get("/monitoring/all")
    assert response.status_code == 200
    items = json.loads(await response.get_data())
    assert 1 == len(items)
    assert "5db11ec55f627d8aa0b545fb" == items[0]["_id"]


async def test_fetch_monitoring_by_companies(client, app):
    response = await client.get('/monitoring/all?q=&where={"company":"5c3eb6975f627db90c84093c"}')
    assert response.status_code == 200
    items = json.loads(await response.get_data())
    assert 1 == len(items)

    response = await client.get('/monitoring/all?q=&where={"company":"6c3eb6975f627db90c84093e"}')
    assert response.status_code == 200
    items = json.loads(await response.get_data())
    assert 0 == len(items)


async def test_post_monitoring(client):
    response = await client.post(
        "/monitoring/new",
        json={
            "is_enabled": True,
            "users": [
                ObjectId("5c53afa45f627d8333220f15"),
                ObjectId("5c4684645f627debec1dc3db"),
            ],
            "company": ObjectId("5c3eb6975f627db90c84093c"),
            "subject": "",
            "name": "W2",
            "_etag": "f023a8db3cdbe31e63ac4b0e6864f5a86ef07253",
            "description": "D3",
            "alert_type": "full_text",
            "query": "hgnhgnhg",
            "schedule": {"interval": "immediate"},
        },
    )
    assert response.status_code == 201
    response = await client.get("/monitoring/all")
    assert response.status_code == 200
    items = json.loads(await response.get_data())
    assert 2 == len(items)
    assert "W1" == items[0]["name"]
    assert "W2" == items[1]["name"]


async def test_always_send_override_for_immediate_monitoring(client):
    response = await client.post(
        "/monitoring/new",
        json={
            "is_enabled": True,
            "users": [
                ObjectId("5c53afa45f627d8333220f15"),
                ObjectId("5c4684645f627debec1dc3db"),
            ],
            "company": ObjectId("5c3eb6975f627db90c84093c"),
            "subject": "",
            "name": "W2",
            "_etag": "f023a8db3cdbe31e63ac4b0e6864f5a86ef07253",
            "description": "D3",
            "alert_type": "full_text",
            "query": "hgnhgnhg",
            "always_send": True,
            "schedule": {"interval": "immediate"},
        },
    )
    assert response.status_code == 201
    response = await client.get("/monitoring/all")
    assert response.status_code == 200
    items = json.loads(await response.get_data())
    assert 2 == len(items)
    assert "W1" == items[0]["name"]
    assert "W2" == items[1]["name"]
    assert not items[1]["always_send"]


async def test_set_monitoring_users(client):
    response = await client.post(
        "/monitoring/5db11ec55f627d8aa0b545fb/users",
        json={"users": [ObjectId("5c53afa45f627d8333220f15")]},
    )
    assert response.status_code == 200
    response = await client.get("/monitoring/all")
    assert response.status_code == 200
    items = json.loads(await response.get_data())
    assert 1 == len(items)
    assert ["5c53afa45f627d8333220f15"] == items[0]["users"]


async def test_set_monitoring_schedule(client):
    response = await client.post(
        "/monitoring/5db11ec55f627d8aa0b545fb/schedule",
        json={"schedule": {"interval": "four_hour"}},
    )
    assert response.status_code == 200
    response = await client.get("/monitoring/all")
    assert response.status_code == 200
    items = json.loads(await response.get_data())
    assert 1 == len(items)
    assert "four_hour" == items[0]["schedule"]["interval"]


async def test_get_companies_with_monitoring_schedules(client):
    response = await client.get("/monitoring/schedule_companies")
    assert response.status_code == 200
    items = json.loads(await response.get_data())
    assert 1 == len(items)
    assert company_id == items[0]["_id"]


@mock.patch("newsroom.monitoring.email_alerts.utcnow", mock_utcnow)
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_send_immediate_alerts(client, app):
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo",
                "headline": "product immediate",
                "products": [{"code": "12345"}],
                "versioncreated": utcnow(),
            }
        ],
    )

    with app.mail.record_messages() as outbox:
        # async with app.test_request_context():
        # async with app.app_context():
        await MonitoringEmailAlerts().run(immediate=True)
        assert_recipients(
            outbox,
            [
                "foo_user2@bar.com",
                "foo_user@bar.com",
            ],
        )
        assert outbox[0].sender == "newsroom@localhost"
        assert outbox[0].subject == "Monitoring Subject"
        assert "Newsroom Monitoring: W1" in outbox[0].body
        assert "monitoring-export.pdf" in outbox[0].attachments[0]


def assert_recipients(outbox, recipients: List[str]):
    outbox_recipients = []
    for o in outbox:
        outbox_recipients.extend(o.recipients)
    assert len(outbox_recipients) == len(recipients)
    for recipient in recipients:
        assert recipient in outbox_recipients


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_send_one_hour_alerts(client, app):
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert w is not None
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "one_hour"}},
        w,
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_yesterday",
                "headline": "product yesterday",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(days=1),
            }
        ],
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_this_hour",
                "headline": "product this hour",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(minutes=30),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        # async with app.app_context():
        await MonitoringEmailAlerts().scheduled_worker(even_now)
        assert_recipients(
            outbox,
            [
                "foo_user2@bar.com",
                "foo_user@bar.com",
            ],
        )
        assert outbox[0].sender == "newsroom@localhost"
        assert outbox[0].subject == "Monitoring Subject"
        assert "Newsroom Monitoring: W1" in outbox[0].body
        assert "monitoring-export.pdf" in outbox[0].attachments[0]


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_send_two_hour_alerts(client, app):
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert w is not None
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}},
        w,
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_yesterday",
                "headline": "product yesterday",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(days=1),
            }
        ],
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_last_hour",
                "headline": "product last hour",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(minutes=90),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        # async with app.app_context():
        await MonitoringEmailAlerts().scheduled_worker(even_now)
        assert_recipients(
            outbox,
            [
                "foo_user2@bar.com",
                "foo_user@bar.com",
            ],
        )
        assert outbox[0].sender == "newsroom@localhost"
        assert outbox[0].subject == "Monitoring Subject"
        assert "Newsroom Monitoring: W1" in outbox[0].body
        assert "monitoring-export.pdf" in outbox[0].attachments[0]


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_send_four_hour_alerts(client, app):
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert w is not None
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "four_hour"}},
        w,
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_yesterday",
                "headline": "product yesterday",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(days=1),
            }
        ],
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_last_hour",
                "headline": "product three hours",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(hours=3),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        # async with app.app_context():
        await MonitoringEmailAlerts().scheduled_worker(even_now)
        assert_recipients(
            outbox,
            [
                "foo_user2@bar.com",
                "foo_user@bar.com",
            ],
        )
        assert outbox[0].sender == "newsroom@localhost"
        assert outbox[0].subject == "Monitoring Subject"
        assert "Newsroom Monitoring: W1" in outbox[0].body
        assert "monitoring-export.pdf" in outbox[0].attachments[0]


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_send_daily_alerts(client, app):
    now = utcnow()
    now = utc_to_local(app.config["DEFAULT_TIMEZONE"], now)
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert w is not None
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {
            "schedule": {
                "interval": "daily",
                "time": (now - timedelta(minutes=1)).strftime("%H:%M"),
            }
        },
        w,
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_yesterday",
                "headline": "product yesterday",
                "products": [{"code": "12345"}],
                "versioncreated": now - timedelta(hours=22),
            }
        ],
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_last_hour",
                "headline": "product three hours",
                "products": [{"code": "12345"}],
                "versioncreated": now - timedelta(hours=3),
            }
        ],
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_four_days",
                "headline": "product four days",
                "products": [{"code": "12345"}],
                "versioncreated": now - timedelta(days=4),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        # async with app.app_context():
        await MonitoringEmailAlerts().run()
        assert_recipients(
            outbox,
            [
                "foo_user2@bar.com",
                "foo_user@bar.com",
            ],
        )
        assert outbox[0].sender == "newsroom@localhost"
        assert outbox[0].subject == "Monitoring Subject"
        assert "Newsroom Monitoring: W1" in outbox[0].body
        assert "monitoring-export.pdf" in outbox[0].attachments[0]


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_send_weekly_alerts(client, app):
    now = utcnow()
    now = utc_to_local(app.config["DEFAULT_TIMEZONE"], now)
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert w is not None
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {
            "schedule": {
                "interval": "weekly",
                "time": (now - timedelta(minutes=1)).strftime("%H:%M"),
                "day": now.strftime("%a").lower(),
            }
        },
        w,
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_yesterday",
                "headline": "product yesterday",
                "products": [{"code": "12345"}],
                "versioncreated": now - timedelta(hours=22),
            }
        ],
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_last_hour",
                "headline": "product three hours",
                "products": [{"code": "12345"}],
                "versioncreated": now - timedelta(hours=3),
            }
        ],
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_four_days",
                "headline": "product four days",
                "products": [{"code": "12345"}],
                "versioncreated": now - timedelta(days=4),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        # async with app.app_context():
        await MonitoringEmailAlerts().run()
        assert_recipients(
            outbox,
            [
                "foo_user2@bar.com",
                "foo_user@bar.com",
            ],
        )
        assert outbox[0].sender == "newsroom@localhost"
        assert outbox[0].subject == "Monitoring Subject"
        assert "Newsroom Monitoring: W1" in outbox[0].body
        assert "monitoring-export.pdf" in outbox[0].attachments[0]


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_send_alerts_respects_last_run_time(client, app):
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert w is not None
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}},
        w,
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_yesterday",
                "headline": "product yesterday",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(days=1),
            }
        ],
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_last_hour",
                "headline": "product last hour",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(minutes=90),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        # async with app.app_context():
        await MonitoringEmailAlerts().scheduled_worker(even_now)
        assert_recipients(
            outbox,
            [
                "foo_user2@bar.com",
                "foo_user@bar.com",
            ],
        )
        assert outbox[0].sender == "newsroom@localhost"
        assert outbox[0].subject == "Monitoring Subject"
        assert "Newsroom Monitoring: W1" in outbox[0].body
        assert "monitoring-export.pdf" in outbox[0].attachments[0]

    with app.mail.record_messages() as newoutbox:
        # async with app.app_context():
        w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
        assert w is not None
        assert w.get("last_run_time") is not None
        last_run_time = local_to_utc(app.config["DEFAULT_TIMEZONE"], even_now)
        assert w["last_run_time"] > (last_run_time - timedelta(minutes=5))
        await MonitoringEmailAlerts().scheduled_worker(last_run_time)
        assert len(newoutbox) == 0


@mock.patch("newsroom.monitoring.email_alerts.utcnow", mock_utcnow)
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_disabled_profile_wont_send_immediate_alerts(client, app):
    await MonitoringProfileService().update("5db11ec55f627d8aa0b545fb", {"is_enabled": False})
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo",
                "headline": "product immediate",
                "products": [{"code": "12345"}],
                "versioncreated": even_now,
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().run(immediate=True)
        assert len(outbox) == 0


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_disabled_profile_wont_send_scheduled_alerts(client, app):
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert w is not None
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}, "is_enabled": False},
        w,
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_yesterday",
                "headline": "product yesterday",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(days=1),
            }
        ],
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_last_hour",
                "headline": "product last hour",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(minutes=90),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().scheduled_worker(even_now)
        assert len(outbox) == 0


@mock.patch("newsroom.monitoring.email_alerts.utcnow", mock_utcnow)
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_always_send_immediate_alerts_wiont_send_default_email(client, app):
    await MonitoringProfileService().update("5db11ec55f627d8aa0b545fb", {"always_send": True})
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo",
                "headline": "product immediate",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(days=31),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().run(immediate=True)
        assert len(outbox) == 0


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_always_send_schedule_alerts(client, app):
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}, "always_send": True},
        w,
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo",
                "headline": "product immediate",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(days=31),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().scheduled_worker(even_now)
        assert len(outbox) > 0
        assert "No content has matched the monitoring profile for this schedule." in outbox[0].body


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_disable_always_send_schedule_alerts(client, app):
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}, "always_send": False},
        w,
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo",
                "headline": "product immediate",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(days=31),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().scheduled_worker(even_now)
        assert len(outbox) == 0


@mock.patch("newsroom.monitoring.email_alerts.utcnow", mock_utcnow)
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_always_send_immediate_alerts(client, app):
    await MonitoringProfileService().update(ObjectId("5db11ec55f627d8aa0b545fb"), {"always_send": False})
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo",
                "headline": "product immediate",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(days=31),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().run(immediate=True)
        assert len(outbox) == 0


@mock.patch("newsroom.monitoring.email_alerts.utcnow", mock_utcnow)
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_last_run_time_always_updated_with_matching_content_immediate(client, app):
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo",
                "headline": "product immediate",
                "products": [{"code": "12345"}],
                "versioncreated": utcnow(),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().run(immediate=True)
        assert_recipients(
            outbox,
            [
                "foo_user2@bar.com",
                "foo_user@bar.com",
            ],
        )
        assert outbox[0].sender == "newsroom@localhost"
        assert outbox[0].subject == "Monitoring Subject"
        assert "Newsroom Monitoring: W1" in outbox[0].body
        assert "monitoring-export.pdf" in outbox[0].attachments[0]
        w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
        assert w is not None
        assert w.get("last_run_time") is not None
        assert w["last_run_time"] > (mock_utcnow() - timedelta(minutes=5))


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_last_run_time_always_updated_with_matching_content_scheduled(client, app):
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert w is not None
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}},
        w,
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_yesterday",
                "headline": "product yesterday",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(days=1),
            }
        ],
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_last_hour",
                "headline": "product last hour",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(minutes=90),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().scheduled_worker(even_now)
        assert_recipients(
            outbox,
            [
                "foo_user2@bar.com",
                "foo_user@bar.com",
            ],
        )
        assert outbox[0].sender == "newsroom@localhost"
        assert outbox[0].subject == "Monitoring Subject"
        assert "Newsroom Monitoring: W1" in outbox[0].body
        assert "monitoring-export.pdf" in outbox[0].attachments[0]
        w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
        assert w is not None
        assert w.get("last_run_time") is not None
        last_run_time = local_to_utc(app.config["DEFAULT_TIMEZONE"], even_now)
        assert w["last_run_time"] > (last_run_time - timedelta(minutes=5))


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_last_run_time_always_updated_with_no_matching_content_immediate(client, app):
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo",
                "headline": "product immediate",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(days=31),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().run(immediate=True)
        assert len(outbox) == 0
        w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
        assert w is not None
        assert w.get("last_run_time") is not None
        assert w["last_run_time"] > (mock_utcnow() - timedelta(minutes=5))


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_last_run_time_always_updated_with_no_matching_content_scheduled(client, app):
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert w is not None
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}},
        w,
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_yesterday",
                "headline": "product yesterday",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(days=31),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().scheduled_worker(even_now)
        assert len(outbox) == 0
        w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
        assert w is not None
        assert w.get("last_run_time") is not None
        last_run_time = local_to_utc(app.config["DEFAULT_TIMEZONE"], even_now)
        assert w["last_run_time"] > (last_run_time - timedelta(minutes=5))


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_last_run_time_always_updated_with_no_users_immediate(client, app):
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    await update_entries_for("monitoring", ObjectId("5db11ec55f627d8aa0b545fb"), {"users": []}, w)

    await create_entries_for(
        "items",
        [
            {
                "_id": "foo",
                "headline": "product immediate",
                "products": [{"code": "12345"}],
                "versioncreated": even_now,
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().run(immediate=True)
        assert len(outbox) == 0
        w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
        assert w is not None
        assert w.get("last_run_time") is not None
        assert w["last_run_time"] > (mock_utcnow() - timedelta(minutes=5))


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_last_run_time_always_updated_with_no_users_scheduled(client, app):
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert w is not None
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}, "users": []},
        w,
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_yesterday",
                "headline": "product yesterday",
                "products": [{"code": "12345"}],
                "versioncreated": even_now,
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().scheduled_worker(even_now)
        assert len(outbox) == 0
        w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
        assert w is not None
        assert w.get("last_run_time") is not None
        last_run_time = local_to_utc(app.config["DEFAULT_TIMEZONE"], even_now)
        assert w["last_run_time"] > (last_run_time - timedelta(minutes=5))


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_will_send_one_hour_alerts_on_odd_hours(client, app):
    now = even_now.replace(hour=3, minute=0)
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert w is not None
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "one_hour"}},
        w,
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_yesterday",
                "headline": "product yesterday",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(days=1),
            }
        ],
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_last_hour",
                "headline": "product last hour",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(minutes=90),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().scheduled_worker(now)
        assert len(outbox) > 0


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_wont_send_two_hour_alerts_on_odd_hours(client, app):
    now = even_now.replace(hour=3, minute=0)
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert w is not None
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}},
        w,
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_yesterday",
                "headline": "product yesterday",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(days=1),
            }
        ],
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_last_hour",
                "headline": "product last hour",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(minutes=90),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().scheduled_worker(now)
        assert len(outbox) == 0


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_wont_send_four_hour_alerts_on_odd_hours(client, app):
    now = even_now.replace(hour=3, minute=0)
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert w is not None
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "four_hour"}},
        w,
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_yesterday",
                "headline": "product yesterday",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(days=1),
            }
        ],
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo_last_hour",
                "headline": "product last hour",
                "products": [{"code": "12345"}],
                "versioncreated": even_now - timedelta(minutes=90),
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().scheduled_worker(now)
        assert len(outbox) == 0


@mock.patch("newsroom.monitoring.email_alerts.utcnow", mock_utcnow)
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_send_immediate_rtf_attachment_alerts(client, app):
    await post_json(
        client,
        "/settings/general_settings",
        {"monitoring_report_logo_path": get_fixture_path("thumbnail.jpg")},
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo",
                "headline": "product immediate",
                "products": [{"code": "12345"}],
                "versioncreated": utcnow(),
                "byline": "Testy McTestface",
                "body_html": "<p>line 1 of the article text\nline 2 of the story\nand a bit more.</p>",
                "source": "AAAA",
            }
        ],
    )
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert w is not None
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {
            "format_type": "monitoring_rtf",
            "alert_type": "linked_text",
            "keywords": ["text"],
        },
        w,
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().run(immediate=True)
        assert_recipients(
            outbox,
            [
                "foo_user2@bar.com",
                "foo_user@bar.com",
            ],
        )
        assert outbox[0].sender == "newsroom@localhost"
        assert outbox[0].subject == "Monitoring Subject"
        assert "Newsroom Monitoring: W1" in outbox[0].body
        assert "monitoring-export.rtf" in outbox[0].attachments[0]


@mock.patch("newsroom.monitoring.email_alerts.utcnow", mock_utcnow)
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_send_immediate_headline_subject_alerts(client, app):
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo",
                "headline": "Article headline about product",
                "products": [{"code": "12345"}],
                "versioncreated": utcnow(),
            }
        ],
    )
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert w is not None
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"headline_subject": True},
        w,
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().run(immediate=True)
        assert_recipients(
            outbox,
            [
                "foo_user2@bar.com",
                "foo_user@bar.com",
            ],
        )
        assert outbox[0].sender == "newsroom@localhost"
        assert outbox[0].subject == "Article headline about product"
        assert "Newsroom Monitoring: W1" in outbox[0].body


@mock.patch("newsroom.monitoring.email_alerts.utcnow", mock_utcnow)
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_send_immediate_email_alerts(client, app):
    await post_json(
        client,
        "/settings/general_settings",
        {"monitoring_report_logo_path": get_fixture_path("thumbnail.jpg")},
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo",
                "version": "1",
                "headline": "product immediate",
                "products": [{"code": "12345"}],
                "versioncreated": utcnow(),
                "byline": "Testy McTestface",
                "body_html": "<p>line 1 of the article text\nline 2 of the story\nand a bit more.</p>"
                '<!-- EMBED START Audio {id: "editor_2"} -->'
                "<figure>"
                '    <audio controls src="/assets.mp3"></audio>'
                "    <figcaption>Assistant Treasurer</figcaption>"
                "</figure>"
                '<!-- EMBED END Audio {id: "editor_2"} -->'
                "<p>Something after the embed",
                "source": "AAAA",
            }
        ],
    )
    await login_public(client)
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert w is not None
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"format_type": "monitoring_email", "alert_type": "full_text", "keywords": ["text"]},
        w,
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().run(immediate=True)
        assert_recipients(
            outbox,
            [
                "foo_user2@bar.com",
                "foo_user@bar.com",
            ],
        )
        assert outbox[0].sender == "newsroom@localhost"
        assert outbox[0].subject == "Monitoring Subject"
        assert "Something after the embed" in outbox[0].body
        ## TODO When code to remove the embeds from email is ported
        # assert 'Assistant Treasurer' not in outbox[0].body
        assert "Newsroom Monitoring: W1" in outbox[0].body


@mock.patch("newsroom.monitoring.email_alerts.utcnow", mock_utcnow)
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_dont_send_immediate_email_alerts_twice(client, app):
    await post_json(
        client,
        "/settings/general_settings",
        {"monitoring_report_logo_path": get_fixture_path("thumbnail.jpg")},
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo",
                "headline": "product immediate",
                "products": [{"code": "12345"}],
                "versioncreated": utcnow(),
                "byline": "Testy McTestface",
                "body_html": "<p>line 1 of the article text\nline 2 of the story\nand a bit more.</p>",
                "source": "AAAA",
                "version": "1",
            }
        ],
    )
    await create_entries_for(
        "history",
        [
            {
                "action": "email",
                "company": ObjectId("5c3eb6975f627db90c84093c"),
                "section": "monitoring",
                "monitoring": ObjectId("5db11ec55f627d8aa0b545fb"),
                "versioncreated": utcnow(),
                "version": "1",
                "item": "foo",
            }
        ],
    )
    await login_public(client)
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().run(immediate=True)
        assert len(outbox) == 0


@mock.patch("newsroom.monitoring.email_alerts.utcnow", mock_utcnow)
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_dont_send_email_to_disabled_users(client, app):
    await create_entries_for(
        "users",
        [
            {
                "_id": ObjectId("5d4ccb7265af3eaa4a8395bc"),
                "email": "boo_user@bar.com",
                "first_name": "Boo_First_name",
                "last_name": "Boo_Last_name",
                "is_enabled": False,
                "receive_email": True,
                "company": ObjectId(company_id),
            },
            {
                "_id": ObjectId("617f257c04bfdad4366b6997"),
                "email": "ringin@bar.com",
                "first_name": "Ring_In_First_name",
                "last_name": "Ring_In_Last_name",
                "is_enabled": True,
                "receive_email": True,
                "company": ObjectId(company_id),
            },
        ],
    )
    w = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert w is not None
    users = [ObjectId("5d4ccb7265af3eaa4a8395bc"), ObjectId("617f257c04bfdad4366b6997")]
    await update_entries_for("monitoring", ObjectId("5db11ec55f627d8aa0b545fb"), {"users": users}, w)

    await create_entries_for(
        "items",
        [
            {
                "_id": "foo",
                "headline": "product immediate",
                "products": [{"code": "12345"}],
                "versioncreated": utcnow(),
                "byline": "Testy McTestface",
                "body_html": "<p>line 1 of the article text\nline 2 of the story\nand a bit more.</p>",
                "source": "AAAA",
            }
        ],
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().run(immediate=True)
        assert len(outbox) == 1
        assert len(outbox[0].recipients) == 1
        assert_recipients(
            outbox,
            ["ringin@bar.com"],
        )


@mock.patch("newsroom.monitoring.email_alerts.utcnow", mock_utcnow)
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_dont_send_email_to_disabled_companies(client, app):
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo",
                "headline": "product immediate",
                "products": [{"code": "12345"}],
                "versioncreated": utcnow(),
                "byline": "Testy McTestface",
                "body_html": "<p>line 1 of the article text\nline 2 of the story\nand a bit more.</p>",
                "source": "AAAA",
            }
        ],
    )
    c = await find_one_by_id("companies", company_id)
    assert c is not None
    await update_entries_for("companies", ObjectId(company_id), {"is_enabled": False}, c)
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().run(immediate=True)
        assert len(outbox) == 0


async def test_save_only_users_belonging_to_company(client, app):
    w = await find_one_by_id("users", "5c53afa45f627d8333220f15")
    await update_entries_for(
        "users", ObjectId("5c53afa45f627d8333220f15"), {"company": ObjectId("5c3eb6975f627db90c84093c")}, w
    )
    await post_json(
        client,
        "/monitoring/5db11ec55f627d8aa0b545fb/users",
        {"users": ["5c53afa45f627d8333220f15", "111111111111111111111111"]},
    )
    m = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert m["users"] == [ObjectId("5c53afa45f627d8333220f15")]


@mock.patch("newsroom.monitoring.email_alerts.utcnow", mock_utcnow)
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_send_profile_email(client, app):
    await post_json(
        client, "/settings/general_settings", {"monitoring_report_logo_path": get_fixture_path("thumbnail.jpg")}
    )
    await create_entries_for(
        "items",
        [
            {
                "_id": "foo",
                "headline": "product immediate",
                "products": [{"code": "12345"}],
                "versioncreated": utcnow(),
                "byline": "Testy McTestface",
                "body_html": "<p>line 1 of the article text\nline 2 of the story\nand a bit more.</p>",
                "source": "AAAA",
            }
        ],
    )
    m = await find_one_by_id("monitoring", "5db11ec55f627d8aa0b545fb")
    assert m is not None
    await update_entries_for(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {
            "email": "atest@a.com,btest@b.com",
            "format_type": "monitoring_email",
            "is_enabled": "true",
        },
        m,
    )
    with app.mail.record_messages() as outbox:
        await MonitoringEmailAlerts().run(immediate=True)
        assert len(outbox) == 3
        assert_recipients(
            outbox,
            ["atest@a.com", "btest@b.com", "foo_user2@bar.com", "foo_user@bar.com"],
        )


async def test_save_monitoring_email(client, app):
    response = await client.post(
        "/monitoring/5db11ec55f627d8aa0b545fb",
        json={"email": "axb.com, a@b.com", "company": ObjectId(company_id), "name": "test"},
    )
    data = json.loads(await response.get_data())
    assert data["email"] == "Invalid email address"
    response = await client.post(
        "/monitoring/5db11ec55f627d8aa0b545fb",
        json={"email": "a@b.com , d@e.com", "company": ObjectId(company_id), "name": "test"},
    )
    data = json.loads(await response.get_data())
    assert data["success"] is True
    response = await client.get("/monitoring/5db11ec55f627d8aa0b545fb")
    data = json.loads(await response.get_data())
    assert data["email"] == "a@b.com,d@e.com"
