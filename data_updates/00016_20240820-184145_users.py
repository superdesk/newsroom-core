# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : eos87
# Creation: 2024-08-20 18:41

from superdesk.commands.data_updates import DataUpdate as _DataUpdate


class DataUpdate(_DataUpdate):
    """
    This data update removes the `id` and `signup_details` fields that exists in some users
    registries for some unknown reason.
    """

    resource = "users"

    def forwards(self, mongodb_collection, mongodb_database):
        found_registries = mongodb_collection.count_documents({"id": {"$exists": True}})
        print(f"Removing `id` field from {found_registries} user registries.")

        mongodb_collection.update_many({"id": {"$exists": True}}, {"$unset": {"id": ""}})

        print("Removing `signup_details` field from all user registries.")
        mongodb_collection.update_many({}, {"$unset": {"signup_details": ""}})

        print("done.")

    def backwards(self, mongodb_collection, mongodb_database):
        pass
