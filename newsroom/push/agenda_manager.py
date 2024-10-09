import logging
from datetime import datetime

from superdesk.utc import utcnow
from superdesk import get_resource_service
from planning.common import WORKFLOW_STATE

from newsroom.wire import url_for_wire
from newsroom.utils import parse_date_str
from newsroom.core import get_current_wsgi_app
from newsroom.agenda.utils import get_latest_available_delivery, TO_BE_CONFIRMED_FIELD

from .tasks import notify_new_wire_item
from .utils import format_qcode_items, get_display_dates, parse_dates, set_dates


logger = logging.getLogger(__name__)


# TODO-ASYNC: revisit when agenda, items and content_api are async


class AgendaManager:
    def init_adhoc_agenda(self, planning, agenda):
        """
        Inits an adhoc agenda item
        """
        # check if there's an existing ad-hoc
        agenda["item_type"] = "planning"

        # planning dates is saved as the dates of the new agenda
        agenda["dates"] = {
            "start": planning["planning_date"],
            "end": planning["planning_date"],
        }

        agenda["state"] = planning["state"]
        if planning.get("pubstatus") == "cancelled":
            agenda["watches"] = []

        return agenda

    def set_metadata_from_event(self, agenda, event, set_doc_id=True):
        """
        Sets agenda metadata from a given event
        """
        parse_dates(event)

        # setting _id of agenda to be equal to event
        if set_doc_id:
            agenda.setdefault("_id", event["guid"])

        agenda["item_type"] = "event"
        agenda["guid"] = event["guid"]
        agenda["event_id"] = event["guid"]
        agenda["recurrence_id"] = event.get("recurrence_id")
        agenda["name"] = event.get("name")
        agenda["slugline"] = event.get("slugline")
        agenda["definition_short"] = event.get("definition_short")
        agenda["definition_long"] = event.get("definition_long")
        agenda["version"] = event.get("version")
        agenda["versioncreated"] = event.get("versioncreated")
        agenda["calendars"] = event.get("calendars")
        agenda["location"] = event.get("location")
        agenda["ednote"] = event.get("ednote")
        agenda["state"] = event.get("state")
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

    def set_metadata_from_planning(self, agenda, planning_item, force_adhoc=False):
        """Sets agenda metadata from a given planning"""

        parse_dates(planning_item)
        set_dates(agenda)

        if not planning_item.get("event_item") or force_adhoc:
            # adhoc planning item
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
            agenda["state"] = planning_item.get("state")
            agenda["state_reason"] = planning_item.get("state_reason")
            agenda["language"] = planning_item.get("language")
            agenda["source"] = planning_item.get("source")

        if planning_item.get("event_item") and force_adhoc:
            agenda["event_id"] = planning_item["event_item"]

        if not agenda.get("planning_items"):
            agenda["planning_items"] = []

        new_plan = False
        plan = next(
            (p for p in (agenda.get("planning_items")) if p.get("guid") == planning_item.get("guid")),
            {},
        )

        if not plan:
            new_plan = True

        agenda_versioncreated: datetime = agenda["versioncreated"]
        plan_versioncreated: datetime = parse_date_str(planning_item.get("versioncreated")) or agenda_versioncreated

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
        plan["firstcreated"] = parse_date_str(planning_item.get("firstcreated")) or agenda["firstcreated"]
        plan["state"] = planning_item.get("state")
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

        return new_plan

    def set_agenda_planning_items(self, agenda, orig_agenda, planning_item, action="add", send_notification=True):
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
                get_resource_service("agenda").notify_agenda_update(
                    agenda, orig_agenda, planning_item, True, planning_item
                )

        agenda["coverages"], coverage_changes = self.get_coverages(
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
            get_resource_service("agenda").notify_agenda_update(agenda, orig_agenda, planning_item, True)

        agenda["display_dates"] = get_display_dates(agenda["planning_items"])
        agenda.pop("_updated", None)

    def get_coverages(self, planning_items, original_coverages, new_plan):
        """
        Returns list of coverages for given planning items
        """

        def get_existing_coverage(id):
            return next((o for o in original_coverages if o["coverage_id"] == id), {})

        def set_delivery(coverage, deliveries, orig_coverage=None):
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
                                _id=d.get("item_id"),
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
                            cov_deliveries[0]["delivery_href"] = app.set_photo_coverage_href(
                                coverage, planning_item, cov_deliveries
                            )
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

                    set_delivery(new_coverage, coverage.get("deliveries"), existing_coverage)
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
                                self.set_item_reference(new_coverage)

                        if (
                            existing_coverage.get("scheduled") != new_coverage.get("scheduled")
                            and existing_coverage.get("workflow_status") != "completed"
                        ):
                            coverage_changes["coverage_modified"] = True

        if len(original_coverages or []) > len(coverages):
            coverage_changes["coverage_cancelled"] = True

        return coverages, coverage_changes

    def set_item_reference(self, coverage):
        """
        Check if the delivery in the passed coverage refers back to the agenda item and coverage.
        If the item is fulfilled after the item is published it will not have this reference
        :param coverage:
        :return:
        """
        if coverage.get("delivery_id") is None:
            return

        item = get_resource_service("items").find_one(req=None, _id=coverage.get("delivery_id"))
        if item:
            if "planning_id" not in item and "coverage_id" not in item:
                service = get_resource_service("content_api")
                service.datasource = "items"
                service.patch(
                    item.get("_id"),
                    updates={
                        "planning_id": coverage.get("planning_id"),
                        "coverage_id": coverage.get("coverage_id"),
                    },
                )
                item["planning_id"] = coverage.get("planning_id")
                item["coverage_id"] = coverage.get("coverage_id")
                notify_new_wire_item.delay(item["_id"], check_topics=False)
