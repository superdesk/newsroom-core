"""
Superdesk Newsroom
==================

:license: GPLv3
"""

import logging
import superdesk
from superdesk import register_resource  # noqa
from typing import Dict, List, Tuple

__version__ = "2.3.0-rc2"

# reuse content api dbs
MONGO_PREFIX = "CONTENTAPI_MONGO"
ELASTIC_PREFIX = "CONTENTAPI_ELASTICSEARCH"

SCHEMA_VERSIONS = {
    "wire": 1,
    "agenda": 3,
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


class Service(superdesk.Service):
    pass
