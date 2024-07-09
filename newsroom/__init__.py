"""
Superdesk Newsroom
==================

:license: GPLv3
"""

import logging
import superdesk
from superdesk import register_resource  # noqa
from typing import Dict, List, Tuple

from newsroom.user_roles import UserRole

__version__ = "2.7.0"

# reuse content api dbs
MONGO_PREFIX = "CONTENTAPI_MONGO"
ELASTIC_PREFIX = "CONTENTAPI_ELASTICSEARCH"

SCHEMA_VERSIONS = {
    "wire": 3,
    "agenda": 5,
}

logging.basicConfig()
logging.getLogger(__name__).setLevel(logging.INFO)


MongoIndexes = Dict[str, Tuple[List[Tuple[str, int]], Dict]]


class Resource(superdesk.Resource):
    mongo_prefix = MONGO_PREFIX
    elastic_prefix = ELASTIC_PREFIX
    mongo_indexes: MongoIndexes = {}
    SUPPORTED_NESTED_SEARCH_FIELDS: List[str] = []

    # Disable resource websocket notifications
    # as we aren't using them in Newshub
    notifications = False

    # by default make resources available to internal users/administrators
    allowed_roles: List[UserRole] = [UserRole.ADMINISTRATOR, UserRole.INTERNAL, UserRole.ACCOUNT_MANAGEMENT]
    allowed_item_roles: List[UserRole] = [UserRole.ADMINISTRATOR, UserRole.INTERNAL, UserRole.ACCOUNT_MANAGEMENT]

    def __init__(self, endpoint_name, app, service, endpoint_schema=None):
        super().__init__(endpoint_name, app, service, endpoint_schema)
        config = app.config["DOMAIN"][endpoint_name]
        config.update(
            {
                "allowed_roles": [role.value for role in self.allowed_roles],
                "allowed_item_roles": [role.value for role in self.allowed_item_roles],
            }
        )


class Service(superdesk.Service):
    pass
