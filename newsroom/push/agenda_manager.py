from inspect import isawaitable
import logging

from superdesk.utc import utcnow
from planning.common import WORKFLOW_STATE

from newsroom.wire import url_for_wire, WireSearchServiceAsync
from newsroom.utils import parse_date_str
from newsroom.core import get_current_wsgi_app

from newsroom.agenda.utils import get_latest_available_delivery, TO_BE_CONFIRMED_FIELD
from newsroom.agenda.notifications import notify_agenda_update

from .tasks import notify_new_wire_item
from .utils import get_display_dates

logger = logging.getLogger(__name__)


# TODO-ASYNC: revisit when agenda, items and content_api are async


class AgendaManager:
    async def set_agenda_planning_items(self, agenda, orig_agenda, planning_item, action="add", send_notification=True):
        """
        Updates the list of planning items of agenda. If action is 'add' then adds the new one.
        And updates the list of coverages
        """

        if action == "remove":
            existing_planning_items = agenda.get("planning_items") or []
            agenda["planning_items"] = [p for p in existing_planning_items if p["guid"] != planning_item["guid"]] or []
            if (
                len(agenda["planning_items"]) < len(existing_planning_items)
                and len(planning_item.get("coverages") or []) > 0
            ):
                await notify_agenda_update(agenda, orig_agenda, planning_item, True, planning_item)

        agenda["coverages"], coverage_changes = await self.get_coverages(
            agenda["planning_items"],
            (orig_agenda or {}).get("coverages") or [],
            planning_item if action == "add" else None,
        )

        if (
            send_notification
            and action != "remove"
            and (
                coverage_changes.get("coverage_added")
                or coverage_changes.get("coverage_cancelled")
                or coverage_changes.get("coverage_modified")
            )
        ):
            await notify_agenda_update(agenda, orig_agenda, planning_item, True)

        agenda["display_dates"] = get_display_dates(agenda["planning_items"])
        agenda.pop("_updated", None)

    async def get_coverages(self, planning_items, original_coverages, new_plan):
        """
        Returns list of coverages for given planning items
        """

        def get_existing_coverage(id):
            return next((o for o in original_coverages if o["coverage_id"] == id), {})

        async def set_delivery(coverage, deliveries, orig_coverage=None):
            cov_deliveries = []
            if coverage["coverage_type"] == "text":
                for d in deliveries or []:
                    cov_deliveries.append(
                        {
                            "delivery_id": d.get("item_id"),
                            "delivery_href": url_for_wire(
                                None,
                                _external=False,
                                section="wire.item",
                                item_id=d.get("item_id"),
                            ),
                            "delivery_state": d.get("item_state"),
                            "sequence_no": d.get("sequence_no") or 0,
                            "publish_time": parse_date_str(d.get("publish_time")),
                        }
                    )
            else:
                if coverage.get("workflow_status") == "completed":
                    if orig_coverage.get("workflow_status") != coverage["workflow_status"]:
                        cov_deliveries.append(
                            {
                                "sequence_no": 0,
                                "delivery_state": "published",
                                "publish_time": (
                                    next(
                                        (parse_date_str(d.get("publish_time")) for d in deliveries),
                                        None,
                                    )
                                    or utcnow()
                                ),
                            }
                        )

                        try:
                            app = get_current_wsgi_app()
                            delivery_href = app.set_photo_coverage_href(coverage, planning_item, cov_deliveries)
                            if isawaitable(delivery_href):
                                delivery_href = await delivery_href
                            cov_deliveries[0]["delivery_href"] = delivery_href
                        except Exception as e:
                            logger.exception(e)
                            logger.error(
                                "Failed to generate delivery_href for coverage={}".format(coverage.get("coverage_id"))
                            )
                    elif len((orig_coverage or {}).get("deliveries") or []) > 0:
                        cov_deliveries.append(orig_coverage["deliveries"][0])

            coverage["deliveries"] = cov_deliveries
            # Sort the deliveries in reverse sequence order here, so sorting required anywhere else
            coverage["deliveries"].sort(key=lambda d: d["sequence_no"], reverse=True)

            # Get latest delivery that was 'published'
            latest_available_delivery = get_latest_available_delivery(coverage) or {}
            coverage["delivery_id"] = latest_available_delivery.get("delivery_id")
            coverage["delivery_href"] = latest_available_delivery.get("delivery_href")
            coverage["publish_time"] = latest_available_delivery.get("publish_time")

        coverages = []
        coverage_changes = {}

        for planning_item in planning_items:
            if planning_item.get("state") != WORKFLOW_STATE.KILLED:
                for coverage in planning_item.get("coverages") or []:
                    existing_coverage = get_existing_coverage(coverage["coverage_id"])
                    coverage_planning = coverage.get("planning") or {}
                    assigned_desk = coverage.get("assigned_desk") or {}
                    assigned_user = coverage.get("assigned_user") or {}
                    new_coverage = {
                        "planning_id": planning_item.get("guid"),
                        "coverage_id": coverage.get("coverage_id"),
                        "scheduled": coverage_planning.get("scheduled"),
                        "coverage_type": coverage_planning.get("g2_content_type"),
                        "workflow_status": coverage.get("workflow_status"),
                        "coverage_status": coverage.get("news_coverage_status", {}).get("name"),
                        "slugline": coverage_planning.get("slugline"),
                        "genre": coverage_planning.get("genre", []),
                        "coverage_provider": (coverage.get("coverage_provider") or {}).get("name"),
                        "watches": existing_coverage.get("watches") or coverage.get("watches", []),
                        "assigned_desk_name": assigned_desk.get("name"),
                        "assigned_desk_email": assigned_desk.get("email"),
                        "assigned_user_name": assigned_user.get("display_name"),
                        "assigned_user_email": assigned_user.get("email"),
                    }

                    if TO_BE_CONFIRMED_FIELD in coverage:
                        new_coverage[TO_BE_CONFIRMED_FIELD] = coverage[TO_BE_CONFIRMED_FIELD]

                    await set_delivery(new_coverage, coverage.get("deliveries") or [], existing_coverage)
                    coverages.append(new_coverage)

                    if (coverage and not existing_coverage) or ((new_plan or {}).get("_id")) == planning_item.get(
                        "_id"
                    ):
                        coverage_changes["coverage_added"] = True
                    else:
                        if coverage["workflow_status"] != existing_coverage["workflow_status"]:
                            if coverage.get("workflow_status") in [
                                WORKFLOW_STATE.CANCELLED,
                                WORKFLOW_STATE.DRAFT,
                            ]:
                                coverage_changes["coverage_cancelled"] = True

                            if new_coverage.get("workflow_status") == "completed":
                                coverage_changes["coverage_modified"] = True
                                await self.set_item_reference(new_coverage)

                        if (
                            existing_coverage.get("scheduled") != new_coverage.get("scheduled")
                            and existing_coverage.get("workflow_status") != "completed"
                        ):
                            coverage_changes["coverage_modified"] = True

        if len(original_coverages or []) > len(coverages):
            coverage_changes["coverage_cancelled"] = True

        return coverages, coverage_changes

    async def set_item_reference(self, coverage):
        """
        Check if the delivery in the passed coverage refers back to the agenda item and coverage.
        If the item is fulfilled after the item is published it will not have this reference
        :param coverage:
        :return:
        """
        if coverage.get("delivery_id") is None:
            return

        wire_service = WireSearchServiceAsync().service
        item = await wire_service.find_by_id(coverage.get("delivery_id"))
        if item is not None and item.planning_id is None and item.coverage_id is None:
            await wire_service.update(
                item.id,
                {
                    "planning_id": coverage.get("planning_id"),
                    "coverage_id": coverage.get("coverage_id"),
                },
            )
            await notify_new_wire_item.delay(item.id, check_topics=False)
