from superdesk.notification import push_notification
from newsroom.auth import get_user, get_user_id

from .module import module  # noqa
from .services import NotificationsService
from .utils import (
    get_initial_notifications,
    get_notifications_with_items,
    save_user_notifications,
    get_user_notifications,
)


__all__ = [
    "NotificationsService",
    "get_initial_notifications",
    "get_notifications_with_items",
    "save_user_notifications",
    "get_user_notifications",
]


def push_user_notification(name, **kwargs):
    push_notification(":".join(map(str, [name, get_user_id()])), **kwargs)


def push_company_notification(name, **kwargs):
    company_id = get_user().get("company")
    push_notification(f"{name}:company-{company_id}", **kwargs)
