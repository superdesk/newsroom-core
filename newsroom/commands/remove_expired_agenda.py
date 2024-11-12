from typing import AsyncGenerator
import logging
from datetime import datetime, timedelta

import click

from superdesk.core import get_app_config
from superdesk.core.utils import date_to_str
from superdesk.resource_fields import ID_FIELD
from superdesk.lock import lock, unlock
from superdesk.utc import utcnow

from newsroom.types import AgendaItem, AgendaItemType
from newsroom.agenda import AgendaItemService
from .cli import newsroom_cli

logger = logging.getLogger(__name__)


@newsroom_cli.command("remove_expired_agenda")
@click.option("-m", "--expiry", "expiry_days", required=False, help="Number of days to determine expiry")
async def remove_expired_agenda_command(expiry_days=None):
    """Remove expired Agenda items

    By default, no Agenda items expire, you can change this with the ``AGENDA_EXPIRY_DAYS`` config.

    Example:
    ::

        $ python manage.py remove_expired_agenda
        $ python manage.py remove_expired_agenda -m 60
        $ python manage.py remove_expired_agenda --expiry 60
    """
    await remove_expired_agenda(expiry_days=expiry_days)


async def remove_expired_agenda(expiry_days=None):
    num_of_days = int(expiry_days) if expiry_days is not None else int(get_app_config("AGENDA_EXPIRY_DAYS", 0))

    if num_of_days == 0:
        logger.info("Expiry days is set to 0, therefor no items will be removed")
        return

    lock_name = "remove_expired_agenda"
    if not lock(lock_name, expire=1800):
        logger.info("Remove expired agenda items task is already running")
        return

    try:
        num_items_removed = await _remove_expired_items(utcnow(), num_of_days)
    finally:
        unlock(lock_name)

    if num_items_removed == 0:
        logger.info("Completed but no items were removed")
    else:
        logger.info(f"Completed removing {num_items_removed} expired agenda items")


async def _remove_expired_items(now: datetime, expiry_days: int):
    """Remove expired Event and/or Planning items from the Agenda collection"""

    logger.info("Starting to remove expired items")
    agenda_service = AgendaItemService()
    expiry_datetime = now - timedelta(days=expiry_days)
    num_items_removed = 0
    async for expired_items in _get_expired_items(expiry_datetime):
        items_to_remove: set[str] = set()

        for item in expired_items:
            logger.info(f"Processing expired item {item.id}")
            items_to_remove |= await _get_expired_chain_ids(item, expiry_datetime)

        if len(items_to_remove):
            logger.info(f"Deleting items: {items_to_remove}")
            num_items_removed += len(items_to_remove)
            await agenda_service.delete_many({ID_FIELD: {"$in": list(items_to_remove)}})

    logger.info("Finished removing expired items from agenda collection")
    return num_items_removed


async def _get_expired_items(expiry_datetime: datetime) -> AsyncGenerator[list[AgendaItem], None]:
    """Get the expired items, based on ``expiry_datetime``"""

    agenda_service = AgendaItemService()
    expiry_datetime_str = date_to_str(expiry_datetime)
    max_loops = get_app_config("MAX_EXPIRY_LOOPS", 50)

    # Filters out Planning items with coverages that have not yet expired
    coverage_scheduled_query = {
        "nested": {
            "path": "coverages",
            "query": {"range": {"coverages.scheduled": {"gt": expiry_datetime_str}}},
        },
    }
    query = {
        "query": {
            "bool": {
                "filter": [{"range": {"dates.end": {"lte": expiry_datetime_str}}}],
                "should": [
                    # Match Events directly (stored from v2.3+)
                    # No more filters required, as we'll query & check planning items separately
                    {"term": {"item_type": "event"}},
                    # Match Planning directly with no associated Event (stored from v2.3+)
                    {
                        "bool": {
                            "filter": [{"term": {"item_type": "planning"}}],
                            "must_not": [
                                {"exists": {"field": "event_id"}},
                                coverage_scheduled_query,
                            ],
                        }
                    },
                    # Match Event and/or Planning items (stored before v2.3 changes to storage)
                    {
                        "bool": {
                            "must_not": [
                                {"exists": {"field": "item_type"}},
                                coverage_scheduled_query,
                            ],
                        }
                    },
                ],
                "minimum_should_match": 1,
            },
        },
        "sort": [{"dates.start": "asc"}],
        "size": get_app_config("MAX_EXPIRY_QUERY_LIMIT", 100),
    }

    for i in range(max_loops):  # avoid blocking forever just in case
        cursor = await agenda_service.search(query)
        items = await cursor.to_list()

        if not len(items):
            break

        yield items
    else:
        logger.warning(f"_get_expired_items did not finish in {max_loops} loops")


def has_plan_expired(item: AgendaItem, expiry_datetime: datetime) -> bool:
    """Returns ``True`` if the maximum planning/coverage time is before or equal to ``expiry_datetime``"""

    max_schedule_datetime = max([coverage.scheduled for coverage in (item.coverages or [])] + [item.dates.end])
    return max_schedule_datetime <= expiry_datetime


async def _get_expired_chain_ids(parent: AgendaItem, expiry_datetime: datetime) -> set[str]:
    """Returns the list of IDs to expire from ``parent`` and it's associated planning items

    If any one item in the chain has not expired, then this function returns an empty array,
    otherwise the list of IDs from the parent and any associated items are returned for purging.
    """

    plan_ids = [plan._id for plan in (parent.planning_items or [])]

    if parent.item_type == AgendaItemType.PLANNING:
        return set() if not has_plan_expired(parent, expiry_datetime) else {parent.id}
    elif not len(plan_ids):
        return {parent.id}

    cursor = await AgendaItemService().search({ID_FIELD: {"$in": plan_ids}}, use_mongo=True)
    items: set[str] = {parent.id}
    async for plan in cursor:
        if not has_plan_expired(plan, expiry_datetime):
            return set()
        items.add(plan.id)

    return items
