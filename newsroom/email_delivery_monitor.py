import logging

from superdesk.celery_task_utils import get_lock_id
from superdesk.core import get_app_config, get_current_app
from superdesk.lock import lock, unlock
from superdesk.utc import utcnow

from newsroom.celery_app import celery
from newsroom.email import send_email


logger = logging.getLogger(__name__)

REDIS_KEY = "newsroom:email_delivery_monitor"


class EmailDeliveryMonitor:
    def __init__(self):
        self.log_msg = "Email delivery monitor"

    def get_recipients(self) -> list[str]:
        recipients = get_app_config("EMAIL_DELIVERY_MONITOR_RECIPIENTS")
        if not recipients:
            return []

        return [recipient.strip() for recipient in recipients.split(",") if recipient.strip()]

    def get_redis(self):
        return getattr(get_current_app().as_any(), "redis", None)

    def record_status(self, status: str, timestamp, recipients: list[str], error: str | None = None) -> None:
        redis = self.get_redis()
        if redis is None:
            return

        payload = {
            "status": status,
            "updated_at": timestamp.isoformat(),
            "last_attempt_at": timestamp.isoformat(),
            "recipient_count": str(len(recipients)),
            "recipients": ",".join(recipients),
        }
        if status == "sent":
            payload["last_success_at"] = timestamp.isoformat()
        if error:
            payload["error"] = error[:500]

        redis.hset(REDIS_KEY, mapping=payload)
        redis.expire(REDIS_KEY, 24 * 60 * 60)

    async def run(self) -> None:
        recipients = self.get_recipients()
        if not recipients:
            logger.info("%s status=skipped reason=no_recipients", self.log_msg)
            return

        lock_name = get_lock_id("newsroom", "email_delivery_monitor")
        if not lock(lock_name, expire=610):
            logger.error("%s status=skipped reason=already_running", self.log_msg)
            return

        try:
            timestamp = utcnow()
            logger.info("%s status=started recipients=%s", self.log_msg, recipients)
            self.record_status("started", timestamp, recipients)

            subject = "Newsroom email delivery monitor"
            text_body = (
                "Email delivery monitor status=ok\n"
                f"timestamp={timestamp.isoformat()}\n"
                f"recipients={', '.join(recipients)}"
            )
            await send_email(to=recipients, subject=subject, text_body=text_body)

            self.record_status("sent", timestamp, recipients)
            logger.info("%s status=sent timestamp=%s recipients=%s", self.log_msg, timestamp.isoformat(), recipients)
        except Exception as exc:
            self.record_status("failed", utcnow(), recipients, error=str(exc))
            logger.exception("%s status=failed recipients=%s", self.log_msg, recipients)
            raise
        finally:
            unlock(lock_name)


@celery.task(soft_time_limit=120)
async def email_delivery_monitor():
    await EmailDeliveryMonitor().run()
