# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : Mark Pittaway
# Creation: 2022-01-04 14:37

from eve.utils import config
from superdesk.commands.data_updates import DataUpdate as _DataUpdate


class DataUpdate(_DataUpdate):
    resource = 'topics'

    def forwards(self, mongodb_collection, mongodb_database):
        for topic in mongodb_collection.find({}):
            if not topic.get('user'):
                pass

            print(mongodb_collection.update(
                {config.ID_FIELD: topic.get(config.ID_FIELD)},
                {
                    '$set': {
                        'original_creator': topic['user'],
                        'version_creator': topic['user'],
                    }
                }
            ))

    def backwards(self, mongodb_collection, mongodb_database):
        for topic in mongodb_collection.find({}):
            print(mongodb_collection.update(
                {config.ID_FIELD: topic.get(config.ID_FIELD)},
                {
                    '$unset': {
                        'original_creator': '',
                        'version_creator': '',
                    }
                }
            ))
