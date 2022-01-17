from bson import ObjectId
import superdesk
import newsroom
from newsroom.utils import set_original_creator, set_version_creator


class TopicsResource(newsroom.Resource):
    url = 'users/<regex("[a-f0-9]{24}"):user>/topics'
    resource_methods = ['GET', 'POST']
    item_methods = ['GET', 'PATCH', 'DELETE']
    internal_resource = True
    schema = {
        'label': {'type': 'string', 'required': True},
        'query': {'type': 'string', 'nullable': True},
        'filter': {'type': 'dict', 'nullable': True},
        'created': {'type': 'dict', 'nullable': True},
        'user': newsroom.Resource.rel('users'),  # This is the owner of the "My Topic"
        'company': newsroom.Resource.rel('companies', required=True),
        'is_global': {'type': 'boolean', 'default': False},
        'subscribers': {
            'type': 'list',
            'schema': newsroom.Resource.rel('users', required=True)
        },
        'timezone_offset': {'type': 'integer', 'nullable': True},
        'topic_type': {'type': 'string', 'nullable': True},
        'navigation': {
            'type': 'list',
            'nullable': True,
            'schema': {'type': 'string'},
        },
        'original_creator': newsroom.Resource.rel('users'),
        'version_creator': newsroom.Resource.rel('users'),
    }


class TopicsService(newsroom.Service):
    def on_create(self, docs):
        super().on_create(docs)
        for doc in docs:
            set_original_creator(doc)
            set_version_creator(doc)

    def on_update(self, updates, original):
        super().on_update(updates, original)
        set_version_creator(updates)

        # If ``is_global`` has been turned off, then remove all subscribers
        # except for the owner of the Topic
        if original.get('is_global') and 'is_global' in updates and not updates.get('is_global'):
            updates['subscribers'] = [original['user']] if original['user'] in original['subscribers'] else []


def get_user_topics(user_id):
    user = superdesk.get_resource_service('users').find_one(req=None, _id=ObjectId(user_id))
    return list(superdesk.get_resource_service('topics').get(req=None, lookup={
        '$or': [
            {'user': user['_id']},
            {
                '$and': [
                    {'company': user.get('company')},
                    {'is_global': True}
                ]
            }
        ]
    }))


def get_wire_notification_topics():
    lookup = {
        '$and': [
            {'subscribers': {'$exists': True, '$ne': []}},
            {'topic_type': 'wire'},
        ]
    }
    return list(superdesk.get_resource_service('topics').get(req=None, lookup=lookup))


def get_agenda_notification_topics(item, users):
    """
    Returns active topics for a given agenda item
    :param item: agenda item
    :param users: active users dict
    :return: list of topics
    """
    lookup = {'$and': [
        {'subscribers': {'$exists': True, '$ne': []}},
        {'topic_type': 'agenda'},
        {'query': item['_id']}
    ]}
    topics = list(superdesk.get_resource_service('topics').get(req=None, lookup=lookup))

    # filter out the topics those belong to inactive users
    return [t for t in topics if users.get(str(t['user']))]
