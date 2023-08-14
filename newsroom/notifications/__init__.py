from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict

import flask
from bson import ObjectId
import superdesk

from superdesk.notification import push_notification
from newsroom.auth import get_user, get_user_id
from .notification_queue import NotificationQueueResource, NotificationQueueService

blueprint = flask.Blueprint("notifications", __name__)


def push_user_notification(name, **kwargs):
    push_notification(":".join(map(str, [name, get_user_id()])), **kwargs)


def push_company_notification(name, **kwargs):
    company_id = get_user().get("company")
    push_notification(f"{name}:company-{company_id}", **kwargs)


class UserNotification(TypedDict):
    resource: str
    action: str
    user: ObjectId
    item: str
    data: Optional[Dict[str, Any]]


def save_user_notifications(entries: List[UserNotification]):
    service = superdesk.get_resource_service("notifications")
    notification_ids = service.post(entries)
    new_notifications = service.get_items(notification_ids)

    # Iterate over the new notifications and collect the number
    # of new notifications per user
    notification_counts: Dict[str, int] = {}
    for entry in new_notifications:
        user_id = str(entry["user"])
        notification_counts.setdefault(user_id, 0)
        notification_counts[user_id] += 1

    # We only send the additional notification counts, and leave it up to the client
    # to request the list of notifications, when required
    push_notification("new_notifications", counts=notification_counts)


from .notifications import (  # noqa: F401,E402
    NotificationsResource,
    NotificationsService,
    get_user_notifications,
)


def init_app(app):
    superdesk.register_resource("notifications", NotificationsResource, NotificationsService, _app=app)
    superdesk.register_resource("notification_queue", NotificationQueueResource, NotificationQueueService, _app=app)
