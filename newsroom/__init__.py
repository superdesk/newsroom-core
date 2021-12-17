"""
Superdesk Newsroom
==================

:license: GPLv3
"""

import logging
import superdesk
from superdesk import register_resource  # noqa

__version__ = '1.15.2'

# reuse content api dbs
MONGO_PREFIX = 'CONTENTAPI_MONGO'
ELASTIC_PREFIX = 'CONTENTAPI_ELASTICSEARCH'

logging.basicConfig()
logging.getLogger(__name__).setLevel(logging.INFO)


class Resource(superdesk.Resource):
    mongo_prefix = MONGO_PREFIX
    elastic_prefix = ELASTIC_PREFIX


class Service(superdesk.Service):
    pass
