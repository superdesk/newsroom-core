from content_api import MONGO_PREFIX

import newsroom


class ClientResource(newsroom.Resource):
    """
    Client schema
    """

    schema = {
        "name": {
            "type": "string",
            "required": True,
            "unique": True,
        },
        "password": {"type": "string", "required": True},
        "last_active": {
            "type": "datetime",
            "required": False,
            "nullable": True
        },
    }

    datasource = {
        'source': 'oauth_clients',
        'default_sort': [('name', 1)]
    }
    item_methods = ['GET', 'PATCH', 'DELETE']
    resource_methods = ['GET', 'POST']
    mongo_prefix = MONGO_PREFIX
    internal_resource = True


class ClientService(newsroom.Service):
    pass
