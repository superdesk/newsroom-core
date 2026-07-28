import datetime
from unittest import mock


from newsroom.email_delivery_monitor import EmailDeliveryMonitor


async def test_email_delivery_monitor_sends_mail(app, caplog):
    caplog.set_level("INFO")
    app.config["EMAIL_DELIVERY_MONITOR_RECIPIENTS"] = "ops@localhost.com, second@localhost.com"

    fixed_now = datetime.datetime(2026, 7, 27, 10, 15, 0)

    with mock.patch("newsroom.email_delivery_monitor.utcnow", return_value=fixed_now):
        with mock.patch.object(app.redis, "hset") as hset_mock, mock.patch.object(app.redis, "expire") as expire_mock:
            with app.mail.record_messages() as outbox:
                async with app.app_context():
                    await EmailDeliveryMonitor().run()

    assert len(outbox) == 1
    message = outbox[0]
    assert message.recipients == ["ops@localhost.com", "second@localhost.com"]
    assert message.subject == "Newsroom email delivery monitor"
    assert "Email delivery monitor status=ok" in message.body
    assert fixed_now.isoformat() in message.body
    assert "status=sent" in caplog.text
    assert hset_mock.call_count == 2
    assert expire_mock.call_count == 2
