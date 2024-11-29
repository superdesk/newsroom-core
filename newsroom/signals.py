from typing import Any
from superdesk.core import AsyncSignal

from newsroom.types import UserResourceModel, CompanyResource

#: Signal for when a wire item is about to be added to the DB
#: param item: New wire item dictionary
#: param is_new: Boolean indicating if this Event is to be created or updated
publish_item = AsyncSignal[dict[str, Any], bool]("publish-item")


#: Signal for when an Event is about to be created or updated in the DB
#: param updated: New event dictionary
#: param updates: A dictionary containing the fields to be updated, or ``None`` if being created
#: param original: A dictionary for the original item, or ``None`` if being created
#: param is_new: Boolean indicating if this Event is to be created or updated
publish_event = AsyncSignal[dict[str, Any], dict[str, Any] | None, dict[str, Any] | None, bool]("publish-event")


#: Signal for when a Planning item is about to be created or updated in the DB
#: param item: New planning item dictionary
#: param is_new: Boolean indicating if this Event is to be created or updated
publish_planning = AsyncSignal[dict[str, Any], bool]("publish-planning")


#: Signal fired before an item is about to be ingested into the system
#: param item: A dictionary of the item to be ingested
#:
#: ..versionadded:: 2.4
#:
push = AsyncSignal[dict[str, Any]]("push")


#: Signal fired after a user has been created
#: param user: The UserResourceModel of the user that was created
#:
#: ..versionadded:: 2.4
#:
user_created = AsyncSignal[UserResourceModel]("user-created")


#: Signal fired after a user has been updated
#: param user: The UserResourceModel of the user that was updated (contains the updated values)
#: param updates: A dictionary containing the fields that were updated
#:
#: ..versionadded:: 2.4
#:
user_updated = AsyncSignal[UserResourceModel, dict[str, Any]]("user-updated")


#: Signal fired after a user has been deleted from the system
#: param user: The UserResourceModel of the user that was deleted
#:
#: ..versionadded:: 2.4
#:
user_deleted = AsyncSignal[UserResourceModel]("user-deleted")


#: Signal fired when a company is about to be created
#: param company: The CompanyResource instance of the company to be created
#:
#: ..versionadded:: 2.5.0
#:
company_create = AsyncSignal[CompanyResource]("company-create")
