# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : Mark Pittaway
# Creation: 2021-11-18 18:11

from eve.utils import config
from superdesk.commands.data_updates import DataUpdate as _DataUpdate
from superdesk import get_resource_service


class DataUpdate(_DataUpdate):
    resource = 'topics'

    def forwards(self, mongodb_collection, mongodb_database):
        users = {
            user['_id']: user
            for user in get_resource_service('users').get(req=None, lookup={})
        }

        for topic in mongodb_collection.find({}):
            if not topic.get("user"):  # this could happen on new cp instances with the mgmt api
                continue
            if users.get(topic["user"]) is None:
                print("Deleting topic of missing user", topic["_id"], topic.get("label"))
                print(mongodb_collection.delete_one({"_id": topic["_id"]}))
            else:
                print("Updating topic of existing user", topic["_id"], topic.get("label"))
                print(mongodb_collection.update(
                    {config.ID_FIELD: topic.get(config.ID_FIELD)},
                    {
                        '$set': {
                            'subscribers': [topic['user']] if topic.get('notifications', False) else [],
                            'company': users[topic['user']].get('company'),
                            'is_global': topic.get('is_global', False),
                        },
                        '$unset': {
                            'notifications': ''
                        }
                    }
                ))

    def backwards(self, mongodb_collection, mongodb_database):
        for topic in mongodb_collection.find({}):
            print(mongodb_collection.update(
                {config.ID_FIELD: topic.get(config.ID_FIELD)},
                {
                    '$set': {
                        'notifications': topic['user'] in (topic.get('subscribers') or [])
                    },
                    '$unset': {
                        'subscribers': '',
                        'company': '',
                        'is_global': ''
                    }
                }
            ))
