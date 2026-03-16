import logging
from contextlib import contextmanager
from typing import Iterator

from superdesk.lock import lock, unlock

from newsroom.celery_app import celery
from newsroom.wire import WireSearchServiceAsync
from newsroom.agenda import AgendaItemService

from .notifications import NotificationManager

logger = logging.getLogger(__name__)
notifier = NotificationManager()
LOCK_EXPIRE_SECONDS = 300


def get_lock_name(service: str, _id: str) -> str:
    return f"notify-{service}-{_id}"


@contextmanager
def task_lock(service: str, _id: str, expire: int = LOCK_EXPIRE_SECONDS) -> Iterator[bool]:
    lock_name = get_lock_name(service, _id)
    acquired = lock(lock_name, expire=expire)
    if not acquired:
        logger.debug("Lock conflict on %s", lock_name)
    try:
        yield acquired
    finally:
        if acquired:
            unlock(lock_name)
            logger.debug("Done with %s", lock_name)


@celery.task
async def notify_new_wire_item(_id: str, check_topics=True) -> None:
    with task_lock("wire", _id) as acquired:
        if not acquired:
            return

        logger.info("Send notifications for wire item %s", _id)
        item = await WireSearchServiceAsync().service.find_by_id(_id)
        if item:
            await notifier.notify_new_item(item.to_dict(), check_topics=check_topics)


@celery.task
async def notify_new_agenda_item(_id: str, check_topics=True, is_new=False) -> None:
    with task_lock("agenda", _id) as acquired:
        if not acquired:
            return

        logger.info("Send notifications for agenda item %s", _id)
        service = AgendaItemService()
        agenda = await service.find_by_id(_id)

        if not agenda:
            return

        if agenda.recurrence_id and agenda.recurrence_id != _id and is_new:
            logger.info("Ignoring recurring event %s", _id)
            return

        agenda_dict = agenda.to_dict()
        await service.enhance_item(agenda_dict)
        await notifier.notify_new_item(agenda_dict, check_topics=check_topics)
