from typing import Dict, List, Optional, Any
from datetime import timedelta

from superdesk import get_resource_service
from superdesk.utc import utcnow
from eve.utils import date_to_str
from newsroom.commands.remove_expired_agenda import (
    has_plan_expired,
    _get_expired_chain_ids,
    remove_expired_agenda,
)


def now_minus_days(days: int):
    return utcnow() - timedelta(days=days)


def gen_plans(item: Dict[str, Any], plan_date: int, coverage_dates: Optional[List[int]] = None) -> Dict[str, Any]:
    item.update(
        {
            "item_type": "planning",
            "dates": {
                "start": now_minus_days(plan_date) - timedelta(hours=1),
                "end": now_minus_days(plan_date),
            },
            "coverages": [
                {"scheduled": date_to_str(now_minus_days(coverage_date))} for coverage_date in coverage_dates or []
            ],
        }
    )

    return item


def gen_event(item: Dict[str, Any], event_end_date: int, plan_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    item.update(
        {
            "item_type": "event",
            "dates": {
                "start": now_minus_days(event_end_date) - timedelta(hours=1),
                "end": now_minus_days(event_end_date),
            },
            "planning_items": [{"_id": plan_id} for plan_id in plan_ids or []],
        }
    )

    return item


def test_has_plan_expired():
    expiry_datetime = now_minus_days(60)

    assert has_plan_expired(gen_plans({"_id": "p61"}, 61), expiry_datetime) is True
    assert has_plan_expired(gen_plans({"_id": "p61"}, 61, [61]), expiry_datetime) is True

    assert has_plan_expired(gen_plans({"_id": "p59"}, 59), expiry_datetime) is False
    assert has_plan_expired(gen_plans({"_id": "p59"}, 59, [61, 59]), expiry_datetime) is False
    assert has_plan_expired(gen_plans({"_id": "p61"}, 61, [61, 59]), expiry_datetime) is False


def test_get_expired_chain_ids(app):
    expiry_datetime = now_minus_days(60)

    plan1 = gen_plans({"_id": "plan1"}, 59)
    plan2 = gen_plans({"_id": "plan2"}, 60)
    event1 = gen_event({"_id": "event1"}, 61)
    event2 = gen_event({"_id": "event2"}, 61, ["plan3", "plan4"])
    event3 = gen_event({"_id": "event3"}, 61, ["plan5"])
    event4 = gen_event({"_id": "event4"}, 61, ["plan6", "plan7"])
    app.data.insert(
        "agenda",
        [
            plan1,
            plan2,
            event1,
            event2,
            gen_plans({"_id": "plan3", "event_id": "event2"}, 62, [62]),
            gen_plans({"_id": "plan4", "event_id": "event2"}, 61, [61]),
            event3,
            gen_plans({"_id": "plan5", "event_id": "event3"}, 59),
            event4,
            gen_plans({"_id": "plan6", "event_id": "event4"}, 61),
            gen_plans({"_id": "plan7", "event_id": "event4"}, 61, [59]),
        ],
    )

    assert _get_expired_chain_ids(plan1, expiry_datetime) == []
    assert _get_expired_chain_ids(plan2, expiry_datetime) == ["plan2"]
    assert _get_expired_chain_ids(event1, expiry_datetime) == ["event1"]
    assert _get_expired_chain_ids(event2, expiry_datetime) == [
        "event2",
        "plan3",
        "plan4",
    ]
    assert _get_expired_chain_ids(event3, expiry_datetime) == []
    assert _get_expired_chain_ids(event4, expiry_datetime) == []


def test_remove_expired_agenda(app):
    app.data.insert(
        "agenda",
        [
            # Items to keep (not yet expired)
            gen_plans({"_id": "plan1"}, 59),
            gen_event({"_id": "event3"}, 61, ["plan5"]),
            gen_plans({"_id": "plan5", "event_id": "event3"}, 59),
            gen_event({"_id": "event4"}, 61, ["plan6", "plan7"]),
            gen_plans({"_id": "plan6", "event_id": "event4"}, 61),
            gen_plans({"_id": "plan7", "event_id": "event4"}, 61, [59]),
            # Items to purge (expired)
            gen_event({"_id": "event1"}, 61),
            gen_plans({"_id": "plan2"}, 60),
            gen_event({"_id": "event2"}, 61, ["plan3", "plan4"]),
            gen_plans({"_id": "plan3", "event_id": "event2"}, 62, [62]),
            gen_plans({"_id": "plan4", "event_id": "event2"}, 61, [61]),
        ],
    )

    ids_to_keep = ["plan1", "plan5", "plan6", "plan7", "event3", "event4"]
    ids_to_purge = ["plan2", "plan3", "plan4", "event1", "event2"]

    # Test with default ``AGENDA_EXPIRY_DAYS=0`` (disable purging)
    agenda_service = get_resource_service("agenda")
    remove_expired_agenda()
    item_ids = [item["_id"] for item in agenda_service.find({})]
    for item_id in ids_to_keep + ids_to_purge:
        assert item_id in item_ids

    # Test with setting ``AGENDA_EXPIRY_DAYS=60`` (as a string)
    app.config["AGENDA_EXPIRY_DAYS"] = "60"
    # remove_expired_agenda(60)
    # item_ids = [item["_id"] for item in agenda_service.find({})]
    # for item_id in ids_to_keep:
    #     assert item_id in item_ids
    # for item_id in ids_to_purge:
    #     assert item_id not in item_ids
