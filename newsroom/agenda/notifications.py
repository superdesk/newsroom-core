from copy import deepcopy
from bson import ObjectId

from newsroom.agenda.email import send_agenda_notification_email
from newsroom.notifications import save_user_notifications
from planning.common import WORKFLOW_STATE

from newsroom.types import UserResourceModel, CompanyResource
from newsroom.utils import get_user_dict_async, get_company_dict_async


def _filter_active_users(
    user_ids: list[str],
    user_dict: dict[ObjectId, UserResourceModel],
    company_dict: dict[ObjectId, CompanyResource],
    events_only: bool = False,
) -> list[ObjectId]:
    active: list[ObjectId] = []
    for user_id_str in user_ids:
        user_id = ObjectId(user_id_str)
        user = user_dict.get(user_id)
        if not user:
            continue

        company = company_dict.get(user.company) if user.company else None

        if user and (not user.company or company):
            if events_only and company and company.events_only:
                continue
            active.append(user_id)
    return active


def _get_detailed_coverage(agenda, original_agenda, cov):
    plan = next(
        (p for p in (agenda.get("planning_items") or []) if p["guid"] == cov.get("planning_id")),
        None,
    )
    if plan and plan.get("state") != WORKFLOW_STATE.KILLED:
        detail_cov = next(
            (c for c in (plan.get("coverages") or []) if c.get("coverage_id") == cov.get("coverage_id")),
            None,
        )
        if detail_cov:
            detail_cov["watches"] = cov.get("watches")

        return detail_cov

    original_cov = next(
        (c for c in original_agenda.get("coverages") or [] if c["coverage_id"] == cov["coverage_id"]),
        cov,
    )
    cov["watches"] = original_cov.get("watches") or []
    return cov


def _fill_all_coverages(
    agenda, original_agenda, coverage_updates, skip_coverages=None, cancelled=False, use_original_agenda=False
):
    if skip_coverages is None:
        skip_coverages = []

    fill_list = coverage_updates["unaltered_coverages"] if not cancelled else coverage_updates["cancelled_coverages"]
    for coverage in (agenda if not use_original_agenda else original_agenda).get("coverages") or []:
        if not next(
            (s for s in skip_coverages if s.get("coverage_id") == coverage.get("coverage_id")),
            None,
        ):
            detailed_coverage = _get_detailed_coverage(agenda, original_agenda, coverage)
            if detailed_coverage:
                fill_list.append(detailed_coverage)


async def notify_agenda_update(
    update_agenda,
    original_agenda,
    item=None,
    events_only=False,
    related_planning_removed=None,
    coverage_updated=None,
):
    if not update_agenda or original_agenda.get("state") == WORKFLOW_STATE.KILLED:
        return

    agenda = deepcopy(update_agenda)
    user_dict = await get_user_dict_async()
    company_dict = await get_company_dict_async()
    coverage_watched = False

    for c in original_agenda.get("coverages") or []:
        if len(c.get("watches") or []) > 0:
            coverage_watched = True
            break

    notify_user_ids = _filter_active_users(original_agenda.get("watches", []), user_dict, company_dict, events_only)
    if len(notify_user_ids) == 0 and not coverage_watched:
        return

    users: list[UserResourceModel] = list(filter(None, [user_dict.get(user_id) for user_id in notify_user_ids]))
    coverage_updates = {
        "modified_coverages": [] if not coverage_updated else [coverage_updated],
        "cancelled_coverages": [],
        "unaltered_coverages": [],
    }

    only_new_coverages = len(coverage_updates["modified_coverages"]) == 0
    time_updated = False
    state_changed = False
    coverage_modified = False

    # Send notification for only these state changes
    notify_states = [
        WORKFLOW_STATE.CANCELLED,
        WORKFLOW_STATE.RESCHEDULED,
        WORKFLOW_STATE.POSTPONED,
        WORKFLOW_STATE.KILLED,
        WORKFLOW_STATE.SCHEDULED,
    ]

    if not coverage_updated:  # If not story updates - but from planning side
        if related_planning_removed:
            _fill_all_coverages(
                agenda, original_agenda, coverage_updates, related_planning_removed.get("coverages") or []
            )
            # Add removed coverages:
            for coverage in related_planning_removed.get("coverages") or []:
                detailed_coverage = _get_detailed_coverage(agenda, original_agenda, coverage)
                if detailed_coverage:
                    coverage_updates["cancelled_coverages"].append(detailed_coverage)
        else:
            # Send notification if time got updated
            if original_agenda.get("dates") and agenda.get("dates"):
                time_updated = (
                    (original_agenda.get("dates") or {}).get("start").replace(tzinfo=None)
                    != (agenda.get("dates") or {}).get("start").replace(tzinfo=None)
                ) or (
                    (original_agenda.get("dates") or {}).get("end").replace(tzinfo=None)
                    != (agenda.get("dates") or {}).get("end").replace(tzinfo=None)
                )

                if agenda.get("state") and agenda.get("state") != original_agenda.get("state"):
                    state_changed = agenda.get("state") in notify_states

                if state_changed:
                    _fill_all_coverages(
                        agenda,
                        original_agenda,
                        coverage_updates,
                        cancelled=False if agenda.get("state") == WORKFLOW_STATE.SCHEDULED else True,
                        use_original_agenda=True,
                    )
                else:
                    if time_updated:
                        _fill_all_coverages(agenda, original_agenda, coverage_updates)
                    else:
                        for coverage in agenda.get("coverages") or []:
                            existing_coverage = next(
                                (
                                    c
                                    for c in original_agenda.get("coverages") or []
                                    if c["coverage_id"] == coverage["coverage_id"]
                                ),
                                None,
                            )
                            detailed_coverage = _get_detailed_coverage(agenda, original_agenda, coverage)
                            if detailed_coverage:
                                if not existing_coverage:
                                    if coverage["workflow_status"] != WORKFLOW_STATE.CANCELLED:
                                        coverage_updates["modified_coverages"].append(detailed_coverage)
                                elif coverage.get(
                                    "workflow_status"
                                ) == WORKFLOW_STATE.CANCELLED and existing_coverage.get(
                                    "workflow_status"
                                ) != coverage.get(
                                    "workflow_status"
                                ):
                                    coverage_updates["cancelled_coverages"].append(detailed_coverage)
                                elif (
                                    (
                                        coverage.get("delivery_state") != existing_coverage.get("delivery_state")
                                        and coverage.get("delivery_state") == "published"
                                    )
                                    or (
                                        coverage.get("workflow_status") != existing_coverage.get("workflow_status")
                                        and coverage.get("workflow_status") == "completed"
                                    )
                                    or (existing_coverage.get("scheduled") != coverage.get("scheduled"))
                                ):
                                    coverage_updates["modified_coverages"].append(detailed_coverage)
                                    only_new_coverages = False
                                elif detailed_coverage["coverage_id"] != (coverage_updated or {}).get("coverage_id"):
                                    coverage_updates["unaltered_coverages"].append(detailed_coverage)

                        # Check for removed coverages - show it as cancelled
                        if item and item.get("type") == "planning":
                            for original_cov in original_agenda.get("coverages") or []:
                                updated_cov = next(
                                    (
                                        c
                                        for c in (agenda.get("coverages") or [])
                                        if c.get("coverage_id") == original_cov.get("coverage_id")
                                    ),
                                    None,
                                )
                                if not updated_cov:
                                    coverage_updates["cancelled_coverages"].append(original_cov)

    if len(coverage_updates["modified_coverages"]) > 0 or len(coverage_updates["cancelled_coverages"]) > 0:
        coverage_modified = True

    if not (coverage_updated or related_planning_removed or time_updated or state_changed or coverage_modified):
        return

    agenda["name"] = agenda.get("name", original_agenda.get("name"))
    agenda["definition_short"] = agenda.get("definition_short", original_agenda.get("definition_short"))
    agenda["ednote"] = agenda.get("ednote", original_agenda.get("ednote"))
    agenda["state_reason"] = agenda.get("state_reason", original_agenda.get("state_reason"))
    action = "been updated."
    if state_changed:
        action = "been {}.".format(
            agenda.get("state") if agenda.get("state") != WORKFLOW_STATE.KILLED else "removed from the calendar"
        )

    if (
        len(coverage_updates["modified_coverages"]) > 0
        and only_new_coverages
        and len(coverage_updates["cancelled_coverages"]) == 0
    ):
        action = "new coverage(s)."

    message = "The {} you have been following has {}".format(
        "event" if agenda.get("event") else "coverage plan", action
    )

    if agenda.get("state_reason"):
        reason_prefix = agenda.get("state_reason").find(":")
        if reason_prefix > 0:
            message = "{} {}".format(
                message,
                agenda["state_reason"][(reason_prefix + 1) : len(agenda["state_reason"])],
            )

    # append coverage watching users too - except for unaltered_coverages
    for c in coverage_updates["cancelled_coverages"] + coverage_updates["modified_coverages"]:
        if c.get("watches"):
            notify_user_ids = _filter_active_users(c["watches"], user_dict, company_dict, events_only)
            users = users + [user_dict[user_id] for user_id in notify_user_ids]

    # Send notifications to users
    await save_user_notifications(
        [
            dict(
                user=user.id,
                item=agenda.get("_id"),
                resource="agenda",
                action="watched_agenda_updated",
                data=None,
            )
            for user in users
        ]
    )

    for user in users:
        await send_agenda_notification_email(
            user.to_dict(),
            agenda,
            message,
            original_agenda,
            coverage_updates,
            related_planning_removed,
            coverage_updated,
            time_updated,
            coverage_modified,
        )
