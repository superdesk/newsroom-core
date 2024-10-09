import logging

from contextlib import contextmanager
from superdesk.lock import lock, unlock
from superdesk import get_resource_service

from newsroom.celery_app import celery
from newsroom.core import get_current_wsgi_app

from .notifications import NotificationManager

logger = logging.getLogger(__name__)
notifier = NotificationManager()


@contextmanager
def locked(_id: str, service: str):
    lock_name = f"notify-{service}-{_id}"
    if not lock(lock_name, expire=300):
        logger.debug(f"Lock conflict on {lock_name}")
        return

    logger.debug("Starting task %s", lock_name)
    try:
        yield lock_name
    finally:
        unlock(lock_name)
        logger.debug("Done with %s", lock_name)


@celery.task
async def notify_new_wire_item(_id, check_topics=True):
    with locked(_id, "wire"):
        item = get_resource_service("items").find_one(req=None, _id=_id)
        if item:
            await notifier.notify_new_item(item, check_topics=check_topics)


@celery.task
async def notify_new_agenda_item(_id, check_topics=True, is_new=False):
    with locked(_id, "agenda"):
        app = get_current_wsgi_app()
        agenda = app.data.find_one("agenda", req=None, _id=_id)

        if agenda:
            if agenda.get("recurrence_id") and agenda.get("recurrence_id") != _id and is_new:
                logger.info("Ignoring recurring event %s", _id)
                return

            get_resource_service("agenda").enhance_items([agenda])
            await notifier.notify_new_item(agenda, check_topics=check_topics)
