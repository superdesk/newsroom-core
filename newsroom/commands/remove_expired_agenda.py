from typing import List, Set, Dict, Any, Generator
import logging
from datetime import datetime, timedelta
from flask import current_app as app, json
from eve.utils import ParsedRequest, date_to_str, config

from superdesk import get_resource_service
from superdesk.lock import lock, unlock
from superdesk.utc import utcnow

from newsroom.utils import parse_date_str
from newsroom.agenda.utils import get_item_type, AGENDA_ITEM_TYPE
from .manager import manager

logger = logging.getLogger(__name__)


@manager.option('-m', '--expiry', dest='expiry_days', required=False)
def remove_expired_agenda(expiry_days=None):
    """Remove expired Agenda items

    By default, no Agenda items expire, you can change this with the ``AGENDA_EXPIRY_DAYS`` config.

    Example:
    ::

        $ python manage.py remove_expired_agenda
        $ python manage.py remove_expired_agenda -m 60
        $ python manage.py remove_expired_agenda --expiry 60
    """

    num_of_days = int(expiry_days) if expiry_days is not None else app.config.get("AGENDA_EXPIRY_DAYS", 0)

    if num_of_days == 0:
        logger.info("Expiry days is set to 0, therefor no items will be removed")
        return

    lock_name = "remove_expired_agenda"
    if not lock(lock_name, expire=1800):
        logger.info("Remove expired agenda items task is already running")
        return

    try:
        num_items_removed = _remove_expired_items(utcnow(), num_of_days)
    finally:
        unlock(lock_name)

    if num_items_removed == 0:
        logger.info("Completed but no items were removed")
    else:
        logger.info(f"Completed removing {num_items_removed} expired agenda items")


def _remove_expired_items(now: datetime, expiry_days: int):
    """Remove expired Event and/or Planning items from the Agenda collection"""

    logger.info("Starting to remove expired items")
    agenda_service = get_resource_service("agenda")
    expiry_datetime = now - timedelta(days=expiry_days)
    num_items_removed = 0
    for expired_items in _get_expired_items(expiry_datetime):
        items_to_remove: Set[str] = set()

        for item in expired_items:
            item_id = item[config.ID_FIELD]
            logger.info(f"Processing expired item {item_id}")
            for child_id in _get_expired_chain_ids(item, expiry_datetime):
                items_to_remove.add(child_id)

        if len(items_to_remove):
            logger.info(f"Deleting items: {items_to_remove}")
            num_items_removed += len(items_to_remove)
            agenda_service.delete_action(lookup={config.ID_FIELD: {"$in": list(items_to_remove)}})

    logger.info("Finished removing expired items from agenda collection")
    return num_items_removed


def _get_expired_items(expiry_datetime: datetime) -> Generator[List[Dict[str, Any]], datetime, None]:
    """Get the expired items, based on ``expiry_datetime``"""

    agenda_service = get_resource_service("agenda")
    max_loops = app.config.get("MAX_EXPIRY_LOOPS", 50)
    ids_processed: Set[str] = set()
    for i in range(max_loops):  # avoid blocking forever just in case
        req = ParsedRequest()
        expiry_datetime_str = date_to_str(expiry_datetime)

        # Filters out Planning items with coverages that have not yet expired
        coverage_scheduled_query = {
            "nested": {
                "path": "coverages",
                "query": {"range": {"coverages.scheduled": {"gt": expiry_datetime_str}}},
            },
        }
        req.args = {
            "source": json.dumps({
                "query": {
                    "bool": {
                        "must": [{"range": {"dates.end": {"lte": expiry_datetime_str}}}],
                        "should": [
                            # Match Events directly (stored from v2.3+)
                            # No more filters required, as we'll query & check planning items separately
                            {"term": {"item_type": "event"}},

                            # Match Planning directly with no associated Event (stored from v2.3+)
                            {"bool": {
                                "must": [{"term": {"item_type": "planning"}}],
                                "must_not": [
                                    {"exists": {"field": "event_id"}},
                                    coverage_scheduled_query,
                                ],
                            }},

                            # Match Event and/or Planning items (stored before v2.3 changes to storage)
                            {"bool": {
                                "must_not": [
                                    {"exists": {"field": "item_type"}},
                                    coverage_scheduled_query,
                                ],
                            }},
                        ],
                        "minimum_should_match": 1,
                    },
                },
                "sort": [{"dates.start": "asc"}],
                "size": app.config.get("MAX_EXPIRY_QUERY_LIMIT", 100),
            }),
        }

        items = list(agenda_service.internal_get(req=req, lookup=None))

        if not len(items):
            break

        for item in items:
            ids_processed.add(item[config.ID_FIELD])

        yield items
    else:
        logger.warning(f"_get_expired_items did not finish in {max_loops} loops")


def has_plan_expired(item: Dict[str, Any], expiry_datetime: datetime) -> bool:
    """Returns ``True`` if the maximum planning/coverage time is before or equal to ``expiry_datetime``"""

    max_schedule_datetime = max(
        [parse_date_str(coverage["scheduled"]) for coverage in (item.get("coverages") or [])] +
        [parse_date_str(item["dates"]["end"])]
    )
    return max_schedule_datetime <= expiry_datetime


def _get_expired_chain_ids(parent: Dict[str, Any], expiry_datetime: datetime) -> List[str]:
    """Returns the list of IDs to expire from ``parent`` and it's associated planning items

    If any one item in the chain has not expired, then this function returns an empty array,
    otherwise the list of IDs from the parent and any associated items are returned for purging.
    """

    item_type = get_item_type(parent)
    plan_ids = [
        plan.get(config.ID_FIELD)
        for plan in (parent.get("planning_items") or [])
    ]

    if item_type == AGENDA_ITEM_TYPE.PLANNING:
        return [] if not has_plan_expired(parent, expiry_datetime) else [parent[config.ID_FIELD]]
    elif not len(plan_ids):
        return [parent[config.ID_FIELD]]

    agenda_service = get_resource_service("agenda")
    items: List[str] = [parent[config.ID_FIELD]]
    for plan in agenda_service.find(where={config.ID_FIELD: {"$in": plan_ids}}):
        if not has_plan_expired(plan, expiry_datetime):
            return []
        items.append(plan[config.ID_FIELD])

    return items
