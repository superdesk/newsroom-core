from typing import cast, Any, Sequence
from datetime import datetime
import logging

from bson import ObjectId

from superdesk.core.resources.cursor import ElasticsearchResourceCursorAsync
from superdesk.core.resources import AsyncResourceService

from planning.common import ASSIGNMENT_WORKFLOW_STATE

from newsroom.types import AgendaItem, AgendaWorkflowState
from newsroom.core import get_current_wsgi_app
from newsroom.utils import parse_date_str, parse_dates

from newsroom.wire import url_for_wire, WireSearchServiceAsync

from .filters import planning_filters, coverage_filters
from .notifications import notify_agenda_update
from .utils import get_latest_available_delivery, push_agenda_item_notification, TO_BE_CONFIRMED_FIELD


logger = logging.getLogger(__name__)


class AgendaItemService(AsyncResourceService[AgendaItem]):
    async def _convert_dicts_to_model(self, docs: Sequence[AgendaItem | dict[str, Any]]) -> list[AgendaItem]:
        items: list[AgendaItem] = []
        for item in docs:
            if isinstance(item, AgendaItem):
                items.append(item)
            elif item.get("type") == "event":
                agenda, _ = self.convert_event_to_agenda_dict({}, item)
                items.append(AgendaItem.from_dict(agenda))
            elif item.get("type") == "planning":
                agenda, _ = await self.convert_planning_to_agenda_dict({}, item, force_adhoc=True, add_coverages=True)
                items.append(AgendaItem.from_dict(agenda))
            else:
                items.append(AgendaItem.from_dict(item))

        return items

    def convert_event_to_agenda_dict(
        self, agenda: dict[str, Any], event: dict[str, Any], set_doc_id: bool = True
    ) -> tuple[dict[str, Any], list[str]]:
        """
        Sets agenda metadata from a given event
        """
        from newsroom.push.utils import format_qcode_items, set_dates, get_event_dates

        app = get_current_wsgi_app()
        if event.get("files"):
            for file_ref in event["files"]:
                if file_ref.get("media"):
                    file_ref.setdefault("href", app.upload_url(file_ref["media"]))

        plan_ids = event.pop("plans", [])
        parse_dates(event)

        # setting _id of agenda to be equal to event
        guid = event.get("guid") or event["_id"]
        if set_doc_id:
            agenda.setdefault("_id", guid)

        agenda["item_type"] = "event"
        agenda["guid"] = guid
        agenda["event_id"] = guid
        agenda["recurrence_id"] = event.get("recurrence_id")
        agenda["name"] = event.get("name")
        agenda["slugline"] = event.get("slugline")
        agenda["definition_short"] = event.get("definition_short")
        agenda["definition_long"] = event.get("definition_long")
        agenda["version"] = event.get("version")
        agenda["versioncreated"] = event.get("versioncreated")
        agenda["calendars"] = event.get("calendars")
        agenda["location"] = event.get("location", [])
        agenda["ednote"] = event.get("ednote")
        agenda["state_reason"] = event.get("state_reason")
        agenda["place"] = event.get("place")
        agenda["subject"] = format_qcode_items(event.get("subject"))
        agenda["products"] = event.get("products")
        agenda["service"] = format_qcode_items(event.get("anpa_category"))
        agenda["event"] = event
        agenda["registration_details"] = event.get("registration_details")
        agenda["invitation_details"] = event.get("invitation_details")
        agenda["language"] = event.get("language")
        agenda["source"] = event.get("source")

        set_dates(agenda)

        agenda["dates"] = get_event_dates(event)

        agenda["state"] = event.get("state") or AgendaWorkflowState.CANCELLED.SCHEDULED
        if event.get("pubstatus") == "cancelled":
            agenda["state"] = AgendaWorkflowState.CANCELLED

        if event.get("planning_items"):
            agenda["planning_items"] = event["planning_items"]
        if event.get("coverages"):
            agenda["coverages"] = event["coverages"]

        return agenda, plan_ids

    async def convert_planning_to_agenda_dict(
        self,
        agenda: dict[str, Any],
        planning_item: dict[str, Any],
        force_adhoc: bool = False,
        add_coverages: bool = False,
    ) -> tuple[dict[str, Any], bool]:
        """Sets agenda metadata from a given planning"""

        from newsroom.push.utils import format_qcode_items, set_dates, get_display_dates
        from newsroom.push.agenda_manager import AgendaManager

        parse_dates(planning_item)
        set_dates(agenda)

        if not planning_item.get("event_item") or force_adhoc:
            # adhoc planning item
            agenda.setdefault("_id", planning_item["guid"])
            agenda.setdefault("guid", planning_item["guid"])
            agenda["item_type"] = "planning"

            # planning dates is saved as the dates of the new agenda
            agenda["dates"] = {
                "start": planning_item["planning_date"],
                "end": planning_item["planning_date"],
            }
            if planning_item.get("pubstatus") == "cancelled":
                agenda["watches"] = []

            agenda["name"] = planning_item.get("name")
            agenda["headline"] = planning_item.get("headline")
            agenda["slugline"] = planning_item.get("slugline")
            agenda["ednote"] = planning_item.get("ednote")
            agenda["place"] = planning_item.get("place")
            agenda["subject"] = format_qcode_items(planning_item.get("subject"))
            agenda["products"] = planning_item.get("products")
            agenda["urgency"] = planning_item.get("urgency")
            agenda["definition_short"] = planning_item.get("description_text") or agenda.get("definition_short")
            agenda["definition_long"] = planning_item.get("abstract") or agenda.get("definition_long")
            agenda["service"] = format_qcode_items(planning_item.get("anpa_category"))
            agenda["state"] = planning_item.get("state") or "scheduled"
            agenda["state_reason"] = planning_item.get("state_reason")
            agenda["language"] = planning_item.get("language")
            agenda["source"] = planning_item.get("source")
            agenda["event_ids"] = [link["_id"] for link in (planning_item.get("related_events") or [])]

            agenda["state"] = planning_item.get("state") or AgendaWorkflowState.CANCELLED.SCHEDULED
            if planning_item.get("pubstatus") == "cancelled":
                agenda["state"] = AgendaWorkflowState.CANCELLED

        if planning_item.get("event_id"):
            agenda["event_id"] = planning_item["event_id"]
        elif planning_item.get("event_item") and force_adhoc:
            agenda["event_id"] = planning_item["event_item"]

        if not agenda.get("planning_items"):
            agenda["planning_items"] = []

        new_plan = False
        plan: dict[str, Any] = next(
            (p for p in (agenda.get("planning_items") or []) if p.get("guid") == planning_item.get("guid")),
            {},
        )

        if not plan:
            new_plan = True

        agenda_versioncreated: datetime = agenda["versioncreated"]
        plan_versioncreated: datetime = parse_date_str(planning_item.get("versioncreated") or agenda_versioncreated)

        plan["_id"] = planning_item.get("_id") or planning_item.get("guid")
        plan["guid"] = planning_item.get("guid")
        plan["slugline"] = planning_item.get("slugline")
        plan["description_text"] = planning_item.get("description_text")
        plan["headline"] = planning_item.get("headline")
        plan["name"] = planning_item.get("name")
        plan["abstract"] = planning_item.get("abstract")
        plan["place"] = planning_item.get("place")
        plan["subject"] = format_qcode_items(planning_item.get("subject"))
        plan["service"] = format_qcode_items(planning_item.get("anpa_category"))
        plan["urgency"] = planning_item.get("urgency")
        plan["planning_date"] = planning_item.get("planning_date")
        plan["coverages"] = planning_item.get("coverages") or []
        plan["ednote"] = planning_item.get("ednote")
        plan["internal_note"] = planning_item.get("internal_note")
        plan["versioncreated"] = plan_versioncreated
        plan["firstcreated"] = parse_date_str(planning_item.get("firstcreated") or agenda["firstcreated"])
        plan["state"] = planning_item.get("state") or "scheduled"
        plan["state_reason"] = planning_item.get("state_reason")
        plan["products"] = planning_item.get("products")
        plan["agendas"] = planning_item.get("agendas")
        plan[TO_BE_CONFIRMED_FIELD] = planning_item.get(TO_BE_CONFIRMED_FIELD)
        plan["language"] = planning_item.get("language")
        plan["source"] = planning_item.get("source")

        if new_plan:
            agenda["planning_items"].append(plan)

        # Update the versioncreated datetime from Planning item if it's newer than the parent item
        try:
            if plan_versioncreated > agenda_versioncreated:
                agenda["versioncreated"] = plan_versioncreated
        except (KeyError, TypeError):
            pass

        if add_coverages:
            agenda["coverages"], _ = await AgendaManager().get_coverages(agenda["planning_items"], [], planning_item)
            agenda["display_dates"] = get_display_dates(agenda["planning_items"])

        return agenda, new_plan

    async def get_by_coverage_id(self, coverage_id: str) -> ElasticsearchResourceCursorAsync[AgendaItem]:
        return cast(
            ElasticsearchResourceCursorAsync,
            await self.search(
                {
                    "query": {
                        "bool": {
                            "filter": [
                                {
                                    "nested": {
                                        "path": "coverages",
                                        "query": {
                                            "bool": {"filter": [{"term": {"coverages.coverage_id": coverage_id}}]}
                                        },
                                    }
                                }
                            ],
                        }
                    }
                }
            ),
        )

    async def enhance_item(self, doc: dict[str, Any]):
        await self.enhance_coverages(doc.get("coverages") or [])
        doc.setdefault("_hits", {})
        doc["_hits"]["matched_event"] = doc.pop("_search_matched_event", False)

        if not doc.get("planning_items"):
            return

        doc["_hits"]["matched_planning_items"] = [plan["_id"] for plan in doc.get("planning_items") or []]

        # Filter based on _inner_hits
        inner_hits = doc.pop("_inner_hits", {})

        # If the search matched the Event
        # then only count Planning based filters when checking ``_inner_hits``
        if doc["_hits"]["matched_event"]:
            inner_hits = {key: val for key, val in inner_hits.items() if key in planning_filters}

        if not inner_hits or not doc.get("planning_items"):
            return

        if len([f for f in inner_hits.keys() if f in coverage_filters]) > 0:
            # Collect hits for 'coverage' and 'coverage_status' separately to other inner_hits
            coverages_by_filter = {
                key: [item.get("coverage_id") for item in items]
                for key, items in inner_hits.items()
                if key in ["coverage", "coverage_status"]
            }
            unique_coverage_ids = set([coverage_id for items in coverages_by_filter.values() for coverage_id in items])
            doc["_hits"]["matched_coverages"] = [
                coverage_id
                for coverage_id in unique_coverage_ids
                if all([coverage_id in items for items in coverages_by_filter.values()])
            ]

        if doc["item_type"] == "planning":
            # If this is a Planning item, then ``inner_hits`` should only include the
            # fields relevant to the Coverages (as this is the only nested field of a Planning item)
            inner_hits = {key: val for key, val in inner_hits.items() if key in planning_filters}

        if len(inner_hits.keys()) > 0:
            # Store matched Planning IDs into matched_planning_items
            # The Planning IDs must be in all supplied ``_inner_hits``
            # In order to be included (i.e. match all nested planning queries)
            items_by_filter = {
                key: [item.get("guid") or item.get("planning_id") for item in items]
                for key, items in inner_hits.items()
            }
            unique_ids = set([item_id for items in items_by_filter.values() for item_id in items])
            doc["_hits"]["matched_planning_items"] = [
                item_id for item_id in unique_ids if all([item_id in items for items in items_by_filter.values()])
            ]

    async def enhance_coverages(self, coverages: list[dict[str, Any]]):
        completed_coverages = [
            c
            for c in coverages
            if c["workflow_status"] == ASSIGNMENT_WORKFLOW_STATE.COMPLETED and len(c.get("deliveries") or []) > 0
        ]
        # Enhance completed coverages in general - add story's abstract/headline/slugline
        text_delivery_ids: list[str] = [
            c["delivery_id"] for c in completed_coverages if c.get("delivery_id") and c.get("coverage_type") == "text"
        ]
        if text_delivery_ids:
            wire_items = await WireSearchServiceAsync().get_items_by_id(text_delivery_ids)
            if await wire_items.count():
                async for item in wire_items:
                    coverage = [c for c in completed_coverages if c.get("delivery_id") == item.id][0]
                    coverage["publish_time"] = item.publish_schedule or item.firstpublished

    async def set_delivery(self, wire_item: dict[str, Any]) -> list[dict[str, Any]]:
        coverage_id = wire_item.get("coverage_id")
        if not coverage_id:
            return []

        cursor = await self.get_by_coverage_id(coverage_id)
        if not await cursor.count():
            return []

        agenda_items = await cursor.to_list_raw()
        agenda_updated_notification_sent = False

        def is_delivery_validated(coverage: dict[str, Any]):
            latest_delivery = get_latest_available_delivery(coverage)

            return (
                (not latest_delivery or not wire_item.get("rewrite_sequence"))
                or ((wire_item.get("rewrite_sequence") or 0) >= latest_delivery.get("sequence_no", 0))
                or (
                    (wire_item.get("publish_schedule") or wire_item.get("firstpublished"))
                    >= latest_delivery.get("publish_time")
                )
            )

        def update_coverage_details(coverage: dict[str, Any]):
            coverage["delivery_id"] = wire_item["guid"]
            coverage["delivery_href"] = url_for_wire(
                None,
                _external=False,
                section="wire.item",
                item_id=wire_item["guid"],
            )
            coverage["workflow_status"] = ASSIGNMENT_WORKFLOW_STATE.COMPLETED
            deliveries = coverage.get("deliveries") or []
            d = next(
                (d for d in deliveries if d.get("delivery_id") == wire_item["guid"]),
                None,
            )
            if d and d.get("delivery_state") != "published":
                d["delivery_state"] = "published"
                publish_time_str: str | None = wire_item.get("publish_schedule") or wire_item.get("firstpublished")
                d["publish_time"] = parse_date_str(publish_time_str) if publish_time_str else None
            return d

        for item in agenda_items:
            # Make sure coverage watches are using ObjectIds
            for c in item.get("coverages") or []:
                if c.get("watches"):
                    c["watches"] = [ObjectId(u) for u in c["watches"]]

            parent_coverage = next(
                (c for c in item.get("coverages") or [] if c["coverage_id"] == wire_item["coverage_id"]), None
            )
            if not parent_coverage or not is_delivery_validated(parent_coverage):
                continue

            delivery = update_coverage_details(parent_coverage)
            planning_item = next(
                (p for p in item.get("planning_items") or [] if p["_id"] == parent_coverage["planning_id"]), None
            )
            planning_updated = False
            if planning_item:
                coverage = next(
                    (c for c in planning_item.get("coverages") or [] if c["coverage_id"] == wire_item["coverage_id"]),
                    None,
                )
                if coverage:
                    planning_updated = True
                    update_coverage_details(coverage)

            if not planning_updated:
                await self.system_update(item["_id"], {"coverages": item["coverages"]})
            else:
                updates = {
                    "coverages": item["coverages"],
                    "planning_items": item["planning_items"],
                }
                await self.system_update(item["_id"], updates)

            updated_agenda = self.find_by_id(item["_id"])
            # Notify agenda to update itself with new details of coverage
            parent_coverage["publish_time"] = wire_item.get("publish_schedule") or wire_item.get("firstpublished")
            await push_agenda_item_notification("new_item", item=item)

            # If published first time, coverage completion will trigger email - not needed now
            if (delivery or {}).get("sequence_no", 0) > 0 and not agenda_updated_notification_sent:
                agenda_updated_notification_sent = True
                await notify_agenda_update(updated_agenda, updated_agenda, None, True, None, parent_coverage)

        return agenda_items
