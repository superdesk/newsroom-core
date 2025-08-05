from superdesk.notification import push_notification

from newsroom.auth.utils import get_user_id_from_request, get_company_from_request

from .module import module  # noqa
from .services import NotificationsService, NotificationQueueService
from .utils import (
    get_initial_notifications,
    get_notifications_with_items,
    save_user_notifications,
    get_user_notifications,
)


__all__ = [
    "NotificationsService",
    "NotificationQueueService",
    "get_initial_notifications",
    "get_notifications_with_items",
    "save_user_notifications",
    "get_user_notifications",
]


def push_user_notification(name, **kwargs):
    user_id = get_user_id_from_request(None)
    push_notification(":".join(map(str, [name, user_id])), **kwargs)


def push_company_notification(name, **kwargs):
    company = get_company_from_request(None)
    if company:
        push_notification(f"{name}:company-{company.id}", **kwargs)
