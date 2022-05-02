# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : Mark Pittaway
# Creation: 2022-05-02 13:45

from bson import ObjectId
from eve.utils import config
from superdesk.commands.data_updates import DataUpdate as _DataUpdate


class DataUpdate(_DataUpdate):

    resource = 'products'

    def forwards(self, mongodb_collection, mongodb_database):
        for product in mongodb_collection.find({}):
            if not product.get("navigations"):
                continue

            print(mongodb_collection.update(
                {config.ID_FIELD: product.get(config.ID_FIELD)},
                {
                    "$set": {
                        "navigations": [
                            ObjectId(nav_id)
                            for nav_id in product.get("navigations")
                        ]
                    }
                }
            ))

    def backwards(self, mongodb_collection, mongodb_database):
        pass
