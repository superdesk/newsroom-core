from newsroom import MONGO_PREFIX
from newsroom.users.service import UsersService
from newsroom.users.model import UserResourceModel

from superdesk.core.module import Module
from superdesk.core.web import EndpointGroup
from superdesk.core.resources import ResourceConfig, MongoIndexOptions, MongoResourceConfig


users_resource_config = ResourceConfig(
    name="users",
    data_class=UserResourceModel,
    service=UsersService,
    mongo=MongoResourceConfig(
        prefix=MONGO_PREFIX,
        indexes=[
            MongoIndexOptions(
                name="email",
                keys=[("email", 1)],
                unique=True,
                collation={"locale": "en", "strength": 2},
            ),
        ],
    ),
)

users_endpoints = EndpointGroup("users", __name__)

module = Module(
    name="newsroom.users",
    resources=[users_resource_config],
    endpoints=[users_endpoints],
)
