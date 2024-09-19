from superdesk.core.module import Module, SuperdeskAsyncApp
from superdesk.core.resources import (
    ResourceConfig,
    RestParentLink,
    RestEndpointConfig,
    MongoResourceConfig,
    MongoIndexOptions,
)

from newsroom.users.module import users_resource_config
from newsroom import MONGO_PREFIX
from .model import Notification
from .services import NotificationsService


notifications_resource_config = ResourceConfig(
    name="notifications",
    data_class=Notification,
    service=NotificationsService,
    default_sort=[("created", -1)],
    mongo=MongoResourceConfig(
        prefix=MONGO_PREFIX,
        indexes=[
            MongoIndexOptions(
                name="user_created",
                keys=[("user", 1), ("created", -1)],
                unique=True,
                collation={"locale": "en", "strength": 2},
            )
        ],
    ),
    rest_endpoints=RestEndpointConfig(
        parent_links=[
            RestParentLink(
                resource_name=users_resource_config.name,
                model_id_field="user",
            ),
        ],
        url="notifications",
        resource_methods=["GET"],
        item_methods=["GET", "PATCH", "DELETE"],
    ),
)


def init_module(app: SuperdeskAsyncApp):
    from superdesk import register_resource
    from .notification_queue import NotificationQueueResource, NotificationQueueService

    register_resource("notification_queue", NotificationQueueResource, NotificationQueueService, _app=app.wsgi)


module = Module(
    name="newsroom.notifications",
    resources=[notifications_resource_config],
    init=init_module,
)
