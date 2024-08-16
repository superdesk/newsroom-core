import os
from typing import List
from quart import json
from pytest import fixture
from bson import ObjectId
from tests.fixtures import PUBLIC_USER_ID
from newsroom.monitoring.email_alerts import MonitoringEmailAlerts
from unittest import mock
from tests.utils import mock_send_email, post_json
from superdesk.utc import utcnow, utc_to_local, local_to_utc
from datetime import timedelta
from superdesk import get_resource_service


company_id = "5c3eb6975f627db90c84093c"
even_now = utcnow().replace(hour=4, minute=0)


def mock_utcnow():
    return utcnow().replace(minute=0)


def get_fixture_path(fixture):
    return os.path.join(os.path.dirname(__file__), "fixtures", fixture)


@fixture(autouse=True)
async def init(app):
    app.data.insert(
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

    app.data.insert(
        "users",
        [
            {
                "_id": ObjectId("5c53afa45f627d8333220f15"),
                "email": "foo_user@bar.com",
                "first_name": "Foo_First_name",
                "is_enabled": True,
                "receive_email": True,
                "company": "",
            },
            {
                "_id": ObjectId("5c4684645f627debec1dc3db"),
                "email": "foo_user2@bar.com",
                "first_name": "Foo_First_name2",
                "is_enabled": True,
                "receive_email": True,
                "company": "",
            },
        ],
    )

    app.data.insert(
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
    user_id = str(PUBLIC_USER_ID)
    async with client.session_transaction() as session:
        session["user"] = user_id
        session["name"] = "public"
        session["user_type"] = "public"

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
    app.data.insert(
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
    assert len(outbox) == len(recipients)
    outbox_recipients = []
    for o in outbox:
        outbox_recipients.extend(o.recipients)
    for recipient in recipients:
        assert recipient in outbox_recipients


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_send_one_hour_alerts(client, app):
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    assert w is not None
    app.data.update(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "one_hour"}},
        w,
    )
    app.data.insert(
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
    app.data.insert(
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
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    assert w is not None
    app.data.update(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}},
        w,
    )
    app.data.insert(
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
    app.data.insert(
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
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    assert w is not None
    app.data.update(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "four_hour"}},
        w,
    )
    app.data.insert(
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
    app.data.insert(
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
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    assert w is not None
    app.data.update(
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
    app.data.insert(
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
    app.data.insert(
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
    app.data.insert(
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
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    assert w is not None
    app.data.update(
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
    app.data.insert(
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
    app.data.insert(
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
    app.data.insert(
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
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    assert w is not None
    app.data.update(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}},
        w,
    )
    app.data.insert(
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
    app.data.insert(
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
        w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
        assert w is not None
        assert w.get("last_run_time") is not None
        last_run_time = local_to_utc(app.config["DEFAULT_TIMEZONE"], even_now)
        assert w["last_run_time"] > (last_run_time - timedelta(minutes=5))
        await MonitoringEmailAlerts().scheduled_worker(last_run_time)
        assert len(newoutbox) == 0


@mock.patch("newsroom.monitoring.email_alerts.utcnow", mock_utcnow)
@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_disabled_profile_wont_send_immediate_alerts(client, app):
    get_resource_service("monitoring").patch(ObjectId("5db11ec55f627d8aa0b545fb"), {"is_enabled": False})
    app.data.insert(
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
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    assert w is not None
    app.data.update(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}, "is_enabled": False},
        w,
    )
    app.data.insert(
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
    app.data.insert(
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
    get_resource_service("monitoring").patch(ObjectId("5db11ec55f627d8aa0b545fb"), {"always_send": True})
    app.data.insert(
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
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    app.data.update(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}, "always_send": True},
        w,
    )
    app.data.insert(
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
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    app.data.update(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}, "always_send": False},
        w,
    )
    app.data.insert(
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
    get_resource_service("monitoring").patch(ObjectId("5db11ec55f627d8aa0b545fb"), {"always_send": False})
    app.data.insert(
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
    app.data.insert(
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
        w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
        assert w is not None
        assert w.get("last_run_time") is not None
        assert w["last_run_time"] > (mock_utcnow() - timedelta(minutes=5))


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_last_run_time_always_updated_with_matching_content_scheduled(client, app):
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    assert w is not None
    app.data.update(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}},
        w,
    )
    app.data.insert(
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
    app.data.insert(
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
        w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
        assert w is not None
        assert w.get("last_run_time") is not None
        last_run_time = local_to_utc(app.config["DEFAULT_TIMEZONE"], even_now)
        assert w["last_run_time"] > (last_run_time - timedelta(minutes=5))


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_last_run_time_always_updated_with_no_matching_content_immediate(client, app):
    app.data.insert(
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
        w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
        assert w is not None
        assert w.get("last_run_time") is not None
        assert w["last_run_time"] > (mock_utcnow() - timedelta(minutes=5))


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_last_run_time_always_updated_with_no_matching_content_scheduled(client, app):
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    assert w is not None
    app.data.update(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}},
        w,
    )
    app.data.insert(
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
        w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
        assert w is not None
        assert w.get("last_run_time") is not None
        last_run_time = local_to_utc(app.config["DEFAULT_TIMEZONE"], even_now)
        assert w["last_run_time"] > (last_run_time - timedelta(minutes=5))


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_last_run_time_always_updated_with_no_users_immediate(client, app):
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    app.data.update("monitoring", ObjectId("5db11ec55f627d8aa0b545fb"), {"users": []}, w)

    app.data.insert(
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
        w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
        assert w is not None
        assert w.get("last_run_time") is not None
        assert w["last_run_time"] > (mock_utcnow() - timedelta(minutes=5))


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_last_run_time_always_updated_with_no_users_scheduled(client, app):
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    assert w is not None
    app.data.update(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}, "users": []},
        w,
    )
    app.data.insert(
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
        w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
        assert w is not None
        assert w.get("last_run_time") is not None
        last_run_time = local_to_utc(app.config["DEFAULT_TIMEZONE"], even_now)
        assert w["last_run_time"] > (last_run_time - timedelta(minutes=5))


@mock.patch("newsroom.email.send_email", mock_send_email)
async def test_will_send_one_hour_alerts_on_odd_hours(client, app):
    now = even_now.replace(hour=3, minute=0)
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    assert w is not None
    app.data.update(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "one_hour"}},
        w,
    )
    app.data.insert(
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
    app.data.insert(
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
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    assert w is not None
    app.data.update(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "two_hour"}},
        w,
    )
    app.data.insert(
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
    app.data.insert(
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
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    assert w is not None
    app.data.update(
        "monitoring",
        ObjectId("5db11ec55f627d8aa0b545fb"),
        {"schedule": {"interval": "four_hour"}},
        w,
    )
    app.data.insert(
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
    app.data.insert(
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
    app.data.insert(
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
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    assert w is not None
    app.data.update(
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
    app.data.insert(
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
    w = app.data.find_one("monitoring", None, _id="5db11ec55f627d8aa0b545fb")
    assert w is not None
    app.data.update(
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
