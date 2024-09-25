from superdesk.core.module import Module
from superdesk.core.resources import (
    ResourceConfig,
    RestParentLink,
    RestEndpointConfig,
    MongoResourceConfig,
    MongoIndexOptions,
)

from newsroom.users.module import users_resource_config
from newsroom import MONGO_PREFIX
from .models import Notification, NotificationQueue
from .services import NotificationQueueService, NotificationsService


notifications_resource_config = ResourceConfig(
    name="notifications",
    data_class=Notification,
    service=NotificationsService,
    default_sort=[("_created", -1)],
    mongo=MongoResourceConfig(
        prefix=MONGO_PREFIX,
        indexes=[
            MongoIndexOptions(
                name="user_created",
                keys=[("user", 1), ("_created", -1)],
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

notification_queue_resource_config = ResourceConfig(
    name="notification_queue",
    data_class=NotificationQueue,
    service=NotificationQueueService,
    mongo=MongoResourceConfig(
        prefix=MONGO_PREFIX,
        indexes=[MongoIndexOptions(name="user_id", keys=[("user", 1)])],
    ),
)

module = Module(
    name="newsroom.notifications", resources=[notifications_resource_config, notification_queue_resource_config]
)
