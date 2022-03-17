
from content_api import MONGO_PREFIX

import newsroom


class CompaniesResource(newsroom.Resource):
    """
    Company schema
    """

    schema = {
        'name': {
            'type': 'string',
            'unique': True,
            'required': True
        },
        'url': {
            'type': 'string'
        },
        'sd_subscriber_id': {
            'type': 'string'
        },
        'is_enabled': {
            'type': 'boolean',
            'default': True
        },
        'contact_name': {
            'type': 'string'
        },
        'contact_email': {
            'type': 'string'
        },
        'phone': {
            'type': 'string'
        },
        'country': {
            'type': 'string'
        },
        'expiry_date': {
            'type': 'datetime',
            'nullable': True,
            'required': False,
        },
        'sections': {
            'type': 'objectid',
        },
        'archive_access': {
            'type': 'boolean',
        },
        'events_only': {
            'type': 'boolean',
            'default': False,
        },
        'company_type': {
            'type': 'string',
            'nullable': True,
        },
        'account_manager': {
            'type': 'string'
        },
        'monitoring_administrator': {
            'type': 'objectid'
        },
        'allowed_ip_list': {
            'type': 'list',
            'mapping': {'type': 'string'}
        },
        'original_creator': newsroom.Resource.rel('users'),
        'version_creator': newsroom.Resource.rel('users'),
    }
    datasource = {
        'source': 'companies',
        'default_sort': [('name', 1)]
    }
    item_methods = ['GET', 'PATCH', 'DELETE']
    resource_methods = ['GET', 'POST']
    mongo_prefix = MONGO_PREFIX
    internal_resource = True
    mongo_indexes = {
        'name_1': ([('name', 1)], {'unique': True, 'collation': {'locale': 'en', 'strength': 2}}),
    }


class CompaniesService(newsroom.Service):
    pass
