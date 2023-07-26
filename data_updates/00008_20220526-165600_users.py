# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : Mark Pittaway
# Creation: 2022-05-26 16:56

from eve.utils import config
from superdesk.commands.data_updates import DataUpdate as _DataUpdate


class DataUpdate(_DataUpdate):
    resource = "users"

    def forwards(self, mongodb_collection, mongodb_database):
        for user in mongodb_collection.find({}):
            if "receive_app_notifications" in user:
                continue

            print(
                mongodb_collection.update(
                    {config.ID_FIELD: user.get(config.ID_FIELD)},
                    {"$set": {"receive_app_notifications": user.get("receive_email", True)}},
                )
            )

    def backwards(self, mongodb_collection, mongodb_database):
        pass
