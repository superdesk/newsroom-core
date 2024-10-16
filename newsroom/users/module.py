from newsroom import MONGO_PREFIX
from newsroom.types import UserResourceModel, UserAuthResourceModel
from newsroom.users.service import UsersService, UsersAuthService

from superdesk.core.module import Module
from superdesk.core.web import EndpointGroup
from superdesk.core.resources import ResourceConfig, MongoIndexOptions, MongoResourceConfig

users_resource_config = ResourceConfig(
    name="users",
    data_class=UserResourceModel,
    service=UsersService,
    default_sort=[("first_name", 1)],
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

users_auth_resource_config = ResourceConfig(
    name="auth_user",
    datasource_name="users",
    data_class=UserAuthResourceModel,
    service=UsersAuthService,
)

users_endpoints = EndpointGroup("users_views", __name__)

module = Module(
    name="newsroom.users",
    resources=[users_resource_config, users_auth_resource_config],
    endpoints=[users_endpoints],
)
