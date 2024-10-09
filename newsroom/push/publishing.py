import logging
from typing import Any, Optional
from copy import copy, deepcopy
from datetime import timedelta

from planning.common import WORKFLOW_STATE

from newsroom import signals
from superdesk.types import Item
from superdesk.utc import utcnow
from superdesk.core import get_app_config
from superdesk import get_resource_service
from superdesk.resource_fields import VERSION
from superdesk.text_utils import get_word_count, get_char_count

from newsroom.utils import parse_date_str
from newsroom.core import get_current_wsgi_app

from .tasks import notify_new_agenda_item
from .agenda_manager import AgendaManager
from .utils import fix_hrefs, fix_updates, get_event_dates, set_dates, validate_event_push


logger = logging.getLogger(__name__)
agenda_manager = AgendaManager()


# TODO-ASYNC: Revisit when agenda and content_api are async


class Publisher:
    async def publish_item(self, doc: Item, original: Item):
        """Duplicating the logic from content_api.publish service."""
        set_dates(doc)

        doc["firstpublished"] = parse_date_str(doc.get("firstpublished"))
        doc["publish_schedule"] = parse_date_str(doc.get("publish_schedule"))
        doc.setdefault("wordcount", get_word_count(doc.get("body_html", "")))
        doc.setdefault("charcount", get_char_count(doc.get("body_html", "")))
        doc["original_id"] = doc["guid"]

        source_expiry = get_app_config("SOURCE_EXPIRY_DAYS") or {}
        if doc.get("source") in source_expiry:
            doc["expiry"] = utcnow().replace(second=0, microsecond=0) + timedelta(days=source_expiry[doc["source"]])

        service = get_resource_service("content_api")
        service.datasource = "items"

        if doc.get("evolvedfrom"):
            parent_item = service.find_one(req=None, _id=doc["evolvedfrom"])
            if parent_item:
                if parent_item.get("original_id"):
                    doc["original_id"] = parent_item["original_id"]
                doc["ancestors"] = copy(parent_item.get("ancestors", []))
                doc["ancestors"].append(doc["evolvedfrom"])
                doc["bookmarks"] = parent_item.get("bookmarks", [])
                doc["planning_id"] = parent_item.get("planning_id")
                doc["coverage_id"] = parent_item.get("coverage_id")
                if parent_item.get("expiry"):
                    doc["expiry"] = parent_item["expiry"]
            else:
                logger.warning(
                    "Failed to find evolvedfrom item %s for %s",
                    doc["evolvedfrom"],
                    doc["guid"],
                )

        if not original and get_app_config("PUSH_FIX_UPDATES"):  # check if there are updates of this item already
            next_item = service.find_one(req=None, evolvedfrom=doc["guid"])
            if next_item:  # there is an update, add missing ancestor
                doc["nextversion"] = next_item["_id"]
                fix_updates(doc, next_item)

        fix_hrefs(doc)
        logger.debug("publishing %s", doc["guid"])
        app = get_current_wsgi_app()
        for assoc in doc.get("associations", {}).values():
            if assoc:
                assoc.setdefault("subscribers", [])
                app.generate_renditions(assoc)

        # If there is a function defined that generates renditions for embedded images call it.
        if getattr(app, "generate_embed_renditions", None):
            app.generate_embed_renditions(doc)

        try:
            if doc.get("coverage_id"):
                agenda_items = await get_resource_service("agenda").set_delivery(doc)
                if agenda_items:
                    [notify_new_agenda_item.delay(item["_id"], check_topics=False) for item in agenda_items]
        except Exception as ex:
            logger.info("Failed to notify new wire item for Agenda watches")
            logger.exception(ex)

        if get_app_config("WIRE_SUBJECT_SCHEME_WHITELIST") and doc.get("subject"):
            doc["subject"] = [
                subject
                for subject in doc["subject"]
                if subject.get("scheme") in get_app_config("WIRE_SUBJECT_SCHEME_WHITELIST")
            ]

        signals.publish_item.send(app, item=doc, is_new=original is None)

        _id = service.create([doc])[0]
        if "associations" not in doc and original is not None and bool(original.get("associations", {})):
            service.patch(_id, updates={"associations": None})
        if "evolvedfrom" in doc and parent_item:
            service.system_update(parent_item["_id"], {"nextversion": _id}, parent_item)
        return _id

    def publish_event(self, event: dict[str, Any], orig: dict[str, Any]):
        logger.debug("publishing event %s", event)
        validate_event_push(orig, event)

        # populate attachments href
        app = get_current_wsgi_app()
        if event.get("files"):
            for file_ref in event["files"]:
                if file_ref.get("media"):
                    file_ref.setdefault("href", app.upload_url(file_ref["media"]))

        _id = event["guid"]
        service = get_resource_service("agenda")
        plan_ids = event.pop("plans", [])

        if not orig:
            # new event
            agenda: dict[str, Any] = {}
            agenda_manager.set_metadata_from_event(agenda, event)
            agenda["dates"] = get_event_dates(event)

            # Retrieve all current Planning items and add them into this Event
            agenda.setdefault("planning_items", [])
            for plan in service.find(where={"_id": {"$in": plan_ids}}):
                planning_item = plan["planning_items"][0]
                agenda["planning_items"].append(planning_item)
                agenda_manager.set_agenda_planning_items(
                    agenda, orig, planning_item, action="add", send_notification=False
                )

                if not plan.get("event_id"):
                    # Make sure the Planning item has an ``event_id`` defined
                    # This can happen when pushing a Planning item before linking to an Event
                    service.system_update(plan["_id"], {"event_id": _id}, plan)

            signals.publish_event.send(app.as_any(), item=agenda, is_new=True)
            _id = service.post([agenda])[0]
        else:
            # replace the original document
            updates = None
            if (
                event.get("state") in [WORKFLOW_STATE.CANCELLED, WORKFLOW_STATE.KILLED]
                or event.get("pubstatus") == "cancelled"
            ):
                # it has been cancelled so don't need to change the dates
                # update the event, the version and the state
                updates = {
                    "event": event,
                    "version": event.get("version", event.get(VERSION)),
                    "state": event["state"],
                    "state_reason": event.get("state_reason"),
                    "planning_items": orig.get("planning_items"),
                    "coverages": orig.get("coverages"),
                }

                if event.get("pubstatus") == "cancelled":
                    # item removed, reset watches on the item
                    updates["watches"] = []

            elif event.get("state") in [
                WORKFLOW_STATE.RESCHEDULED,
                WORKFLOW_STATE.POSTPONED,
            ]:
                # schedule is changed, recalculate the dates, planning id and coverages from dates will be removed
                updates = {}
                agenda_manager.set_metadata_from_event(updates, event, False)
                updates["dates"] = get_event_dates(event)
                updates["coverages"] = None
                updates["planning_items"] = None

            elif parse_date_str(event.get("versioncreated")) > orig.get("versioncreated"):  # type: ignore
                # event is reposted (possibly after a cancel)
                logger.info("Updating event %s", orig["_id"])
                updates = {
                    "event": event,
                    "version": event.get("version", event.get(VERSION)),
                    "state": event["state"],
                    "dates": get_event_dates(event),
                    "planning_items": orig.get("planning_items"),
                    "coverages": orig.get("coverages"),
                }

                agenda_manager.set_metadata_from_event(updates, event, False)

            else:
                logger.info("Ignoring event %s", orig["_id"])

            if updates:
                updated = orig.copy()
                updated.update(updates)
                signals.publish_event.send(app.as_any(), item=updated, updates=updates, orig=orig, is_new=False)
                service.patch(orig["_id"], updates)
                updates["_id"] = orig["_id"]
                get_resource_service("agenda").notify_agenda_update(updates, orig)

        return _id

    def publish_planning_item(self, planning: dict[str, Any], orig: dict[str, Any]):
        service = get_resource_service("agenda")
        agenda = deepcopy(orig)

        agenda_manager.init_adhoc_agenda(planning, agenda)

        # Update agenda metadata
        new_plan = agenda_manager.set_metadata_from_planning(agenda, planning, force_adhoc=True)

        # Add the planning item to the list
        agenda_manager.set_agenda_planning_items(agenda, orig, planning, action="add" if new_plan else "update")
        app = get_current_wsgi_app()

        if not agenda.get("_id"):
            # Setting ``_id`` of Agenda to be equal to the Planning item if there's no Event ID
            agenda.setdefault("_id", planning["guid"])
            agenda.setdefault("guid", planning["guid"])
            signals.publish_planning.send(app.as_any(), item=agenda, is_new=new_plan)
            return service.post([agenda])[0]
        else:
            # Replace the original
            signals.publish_planning.send(app.as_any(), item=agenda, is_new=new_plan)
            service.patch(agenda["_id"], agenda)
            return agenda["_id"]

    def publish_planning_into_event(self, planning: dict[str, Any]) -> Optional[str]:
        if not planning.get("event_item"):
            return None

        service = get_resource_service("agenda")

        event_id = planning["event_item"]
        plan_id = planning["guid"]
        orig_agenda = service.find_one(req=None, _id=event_id)

        if not orig_agenda:
            # Item not found using ``event_item`` attribute
            # Try again using ``guid`` attribute
            orig_agenda = service.find_one(req=None, _id=plan_id)

        if (orig_agenda or {}).get("item_type") != "event":
            # event id exists in planning item but event is not in the system
            logger.warning(f"Event '{event_id}' for Planning '{plan_id}' not found")
            return None

        agenda = deepcopy(orig_agenda)

        if (
            planning.get("state") in [WORKFLOW_STATE.CANCELLED, WORKFLOW_STATE.KILLED]
            or planning.get("pubstatus") == "cancelled"
        ):
            # Remove the Planning item from the list
            agenda_manager.set_agenda_planning_items(agenda, orig_agenda, planning, action="remove")
            service.patch(agenda["_id"], agenda)
            return None

        # Update agenda metadata
        new_plan = agenda_manager.set_metadata_from_planning(agenda, planning)

        # Add the Planning item to the list
        agenda_manager.set_agenda_planning_items(agenda, orig_agenda, planning, action="add" if new_plan else "update")

        if not agenda.get("_id"):
            # setting _id of agenda to be equal to planning if there's no event id
            agenda.setdefault("_id", planning.get("event_item", planning["guid"]) or planning["guid"])
            agenda.setdefault("guid", planning.get("event_item", planning["guid"]) or planning["guid"])
            return service.post([agenda])[0]
        else:
            # Replace the original document
            service.patch(agenda["_id"], agenda)
            return agenda["_id"]
