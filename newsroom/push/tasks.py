import logging

from contextlib import contextmanager
from superdesk.lock import lock, unlock

from newsroom.celery_app import celery
from newsroom.wire import WireSearchServiceAsync
from newsroom.agenda import AgendaItemService

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
        logger.info("Send notifications for wire item %s", _id)
        item = await WireSearchServiceAsync().service.find_by_id(_id)
        if item:
            await notifier.notify_new_item(item.to_dict(), check_topics=check_topics)


@celery.task
async def notify_new_agenda_item(_id, check_topics=True, is_new=False):
    with locked(_id, "agenda"):
        logger.info("Send notifications for agenda item %s", _id)
        service = AgendaItemService()
        agenda = await service.find_by_id(_id)

        if not agenda:
            return

        if agenda.recurrence_id and agenda.recurrence_id != _id and is_new:
            logger.info("Ignoring recurring event %s", _id)
            return

        agenda_dict = agenda.to_dict()
        await AgendaItemService().enhance_item(agenda_dict)
        await notifier.notify_new_item(agenda_dict, check_topics=check_topics)
