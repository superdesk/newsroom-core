import logging
from typing import Any, Optional
from copy import deepcopy
from datetime import timedelta

from superdesk.types import Item
from superdesk.utc import utcnow
from superdesk.core import get_app_config
from superdesk.resource_fields import VERSION, ID_FIELD, GUID_FIELD
from superdesk.text_utils import get_word_count, get_char_count

from content_api.publish.utils import process_associations

from planning.common import WORKFLOW_STATE

from newsroom import signals
from newsroom.core import get_current_wsgi_app
from newsroom.types import WireItem, AgendaItemType
from newsroom.utils import parse_date_str
from newsroom.wire import WireSearchServiceAsync
from newsroom.agenda import AgendaItemService
from newsroom.agenda.notifications import notify_agenda_update

from .tasks import notify_new_agenda_item
from .agenda_manager import AgendaManager
from .utils import fix_hrefs, fix_updates, set_dates, validate_event_push


logger = logging.getLogger(__name__)
agenda_manager = AgendaManager()


class Publisher:
    async def publish_item(self, doc: Item, original: Item):
        """Duplicating the logic from content_api.publish service."""
        set_dates(doc)

        if doc.get("firstpublished"):
            # If ``firstpublished`` is not defined, it will default to now (in the model)
            doc["firstpublished"] = parse_date_str(doc.get("firstpublished"))

        doc["publish_schedule"] = parse_date_str(doc.get("publish_schedule"))
        doc.setdefault("wordcount", get_word_count(doc.get("body_html", "")))
        doc.setdefault("charcount", get_char_count(doc.get("body_html", "")))
        doc["original_id"] = doc["guid"]

        source_expiry = get_app_config("SOURCE_EXPIRY_DAYS") or {}
        if doc.get("source") in source_expiry:
            doc["expiry"] = utcnow().replace(second=0, microsecond=0) + timedelta(days=source_expiry[doc["source"]])

        wire_search = WireSearchServiceAsync()
        parent_item = None
        if doc.get("evolvedfrom"):
            parent_item = await wire_search.service.find_by_id(doc["evolvedfrom"])
            if parent_item:
                if parent_item.original_id:
                    doc["original_id"] = parent_item.original_id
                doc["ancestors"] = (parent_item.ancestors or []).copy()
                doc["ancestors"].append(doc["evolvedfrom"])
                doc["bookmarks"] = parent_item.bookmarks or []
                doc["planning_id"] = parent_item.planning_id
                doc["coverage_id"] = parent_item.coverage_id
                if parent_item.expiry:
                    doc["expiry"] = parent_item.expiry
            else:
                logger.warning(
                    "Failed to find evolvedfrom item %s for %s",
                    doc["evolvedfrom"],
                    doc["guid"],
                )

        if not original and get_app_config("PUSH_FIX_UPDATES"):  # check if there are updates of this item already
            next_item = await wire_search.service.find_one(evolvedfrom=doc["guid"])
            if next_item:  # there is an update, add missing ancestor
                doc["nextversion"] = next_item.id
                await fix_updates(doc, next_item)

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
                agenda_items = await AgendaItemService().set_delivery(doc)
                if agenda_items:
                    [await notify_new_agenda_item.delay(item["_id"], check_topics=False) for item in agenda_items]
        except Exception as ex:
            logger.info("Failed to notify new wire item for Agenda watches")
            logger.exception(ex)

        if get_app_config("WIRE_SUBJECT_SCHEME_WHITELIST") and doc.get("subject"):
            doc["subject"] = [
                subject
                for subject in doc["subject"]
                if subject.get("scheme") in get_app_config("WIRE_SUBJECT_SCHEME_WHITELIST")
            ]

        await signals.publish_item.send(doc, original is None)

        doc_id = await self.publish_doc_to_content_api(doc)
        if "evolvedfrom" in doc and parent_item:
            await wire_search.service.system_update(parent_item.id, {"nextversion": doc_id})
        return doc_id

    async def publish_doc_to_content_api(self, item_dict: dict[str, Any]) -> str:
        # Copied from content_api.publish.utils.publish_doc_to_content_api
        wire_search = WireSearchServiceAsync()
        service = wire_search.service
        item_dict[ID_FIELD] = item_dict.pop(GUID_FIELD)
        item = WireItem.from_dict(item_dict)

        original = await service.find_by_id(item.id)
        if original:
            item.subscribers = list(set(original.subscribers or []) | set(item.subscribers or []))

        process_associations(item, original)

        if original:
            await service.update(original.id, item.to_dict(context={"use_objectid": True}))
            return original.id
        else:
            return (await service.create([item]))[0].id

    async def publish_event(self, event: dict[str, Any], orig: dict[str, Any]):
        logger.debug("publishing event %s", event)
        validate_event_push(orig, event)

        # populate attachments href
        app = get_current_wsgi_app()
        if event.get("files"):
            for file_ref in event["files"]:
                if file_ref.get("media"):
                    file_ref.setdefault("href", app.upload_url(file_ref["media"]))

        agenda_id = event["guid"]
        service = AgendaItemService()

        if not orig:
            # new event
            agenda, plan_ids = service.convert_event_to_agenda_dict({}, event)

            # Retrieve all current Planning items and add them into this Event
            agenda.setdefault("planning_items", [])
            agenda.setdefault("planning_ids", [])
            for plan in await (await service.search({"_id": {"$in": plan_ids}}, use_mongo=True)).to_list_raw():
                planning_item = plan["planning_items"][0]
                agenda["planning_items"].append(planning_item)
                await agenda_manager.set_agenda_planning_items(
                    agenda, orig, planning_item, action="add", send_notification=False
                )

                if not plan.get("event_id"):
                    # Make sure the Planning item has an ``event_id`` defined
                    # This can happen when pushing a Planning item before linking to an Event
                    await service.system_update(plan["_id"], {"event_id": agenda_id})

            await signals.publish_event.send(agenda, None, None, True)
            agenda_id = (await service.create([agenda]))[0].id
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
                updates, _ = service.convert_event_to_agenda_dict({}, event, set_doc_id=False)
                updates["coverages"] = None
                updates["planning_items"] = None

            elif parse_date_str(event.get("versioncreated")) > orig.get("versioncreated"):  # type: ignore
                # event is reposted (possibly after a cancel)
                logger.info("Updating event %s", orig["_id"])
                updates = {
                    "event": event,
                    "version": event.get("version", event.get(VERSION)),
                    "state": event["state"],
                    # "dates": get_event_dates(event),
                    "planning_items": orig.get("planning_items"),
                    "coverages": orig.get("coverages"),
                }

                service.convert_event_to_agenda_dict(updates, event, set_doc_id=False)

            else:
                logger.info("Ignoring event %s", orig["_id"])

            if updates:
                updated = orig.copy()
                updated.update(updates)
                await signals.publish_event.send(updated, updates, orig, False)
                await service.update(orig["_id"], updates)
                updates["_id"] = orig["_id"]
                await notify_agenda_update(updates, orig)

        return agenda_id

    async def publish_planning_item(self, planning: dict[str, Any], orig: dict[str, Any]):
        service = AgendaItemService()
        agenda = deepcopy(orig)

        # Update agenda metadata
        _, new_plan = await service.convert_planning_to_agenda_dict(agenda, planning, force_adhoc=True)

        # Add the planning item to the list
        await agenda_manager.set_agenda_planning_items(agenda, orig, planning, action="add" if new_plan else "update")

        if not orig.get("_id"):
            # Setting ``_id`` of Agenda to be equal to the Planning item if there's no Event ID
            agenda.setdefault("_id", planning["guid"])
            agenda.setdefault("guid", planning["guid"])
            await signals.publish_planning.send(agenda, new_plan)
            return (await service.create([agenda]))[0].id
        else:
            # Replace the original
            await signals.publish_planning.send(agenda, new_plan)
            await service.update(agenda["_id"], agenda)
            return agenda["_id"]

    async def publish_planning_into_event(self, planning: dict[str, Any]) -> Optional[str]:
        if not planning.get("event_item"):
            return None

        service = AgendaItemService()

        event_id = planning["event_item"]
        plan_id = planning["guid"]

        orig_agenda: dict[str, Any] | None = None
        event = await service.find_by_id(event_id)
        if event:
            orig_agenda = event.to_dict()
        else:
            # Item not found using ``event_item`` attribute
            # Try again using ``guid`` attribute
            plan = await service.find_by_id(plan_id)
            if plan:
                orig_agenda = plan.to_dict()

        if orig_agenda is None or (orig_agenda or {}).get("item_type") != "event":
            # event id exists in planning item but event is not in the system
            logger.warning(f"Event '{event_id}' for Planning '{plan_id}' not found")
            return None

        agenda = deepcopy(orig_agenda)

        if (
            planning.get("state") in [WORKFLOW_STATE.CANCELLED, WORKFLOW_STATE.KILLED]
            or planning.get("pubstatus") == "cancelled"
        ):
            # Remove the Planning item from the list
            await agenda_manager.set_agenda_planning_items(agenda, orig_agenda, planning, action="remove")
            await service.update(agenda["_id"], agenda)
            return None

        if planning and planning.get("guid") not in event.planning_ids:
            agenda["planning_ids"] = event.planning_ids + [planning["guid"]]

        # Update agenda metadata
        _, new_plan = await service.convert_planning_to_agenda_dict(agenda, planning)
        # new_plan = agenda_manager.set_metadata_from_planning(agenda, planning)

        # Add the Planning item to the list
        await agenda_manager.set_agenda_planning_items(
            agenda, orig_agenda, planning, action="add" if new_plan else "update"
        )

        if not agenda.get("_id"):
            # setting _id of agenda to be equal to planning if there's no event id
            agenda.setdefault("_id", planning.get("event_item", planning["guid"]) or planning["guid"])
            agenda.setdefault("guid", planning.get("event_item", planning["guid"]) or planning["guid"])
            return (await service.create([agenda]))[0].id
        else:
            # Replace the original document
            await service.update(agenda["_id"], agenda)
            return agenda["_id"]

    async def publish_planning_related_events(self, planning: dict[str, Any], related_event: dict[str, Any]):
        if not related_event.get("link_type") == "secondary":
            return None

        service = AgendaItemService()
        event_id = related_event.get("_id")

        event = await service.find_by_id(event_id)
        updates: dict[str, Any] = {}

        if event.item_type == AgendaItemType.EVENT and planning and planning.get("guid") not in event.planning_ids:
            updates["planning_ids"] = event.planning_ids + [planning["guid"]]

        planning_item = await service.find_by_id(planning["guid"])
        if planning_item and planning_item.coverages:
            existing_coverages = {c.coverage_id: c for c in event.coverages}
            new_coverages = {c.coverage_id: c for c in planning_item.coverages}

            merged_coverages = {**existing_coverages, **new_coverages}.values()

            updates["coverages"] = list(merged_coverages)

        await service.update(event_id, updates)
