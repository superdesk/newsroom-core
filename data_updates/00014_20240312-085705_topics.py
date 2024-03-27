# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : petr
# Creation: 2024-03-12 08:57

from superdesk.commands.data_updates import DataUpdate as _DataUpdate


class DataUpdate(_DataUpdate):
    resource = "topics"

    def forwards(self, mongodb_collection, mongodb_database):
        user_ids = mongodb_database["users"].distinct("_id")

        # remove missing user private topics
        print(
            "DELETE PRIVATE TOPICS",
            mongodb_database["topics"].delete_many({"user": {"$nin": user_ids}, "is_global": False}).deleted_count,
        )

        # remove missing subscribers
        missing_subscribers = {"subscribers": {"$elemMatch": {"user_id": {"$nin": user_ids}}}}
        print(
            "REMOVE MISSING SUBSCRIBERS",
            mongodb_database["topics"]
            .update_many(missing_subscribers, {"$pull": {"subscribers": {"user_id": {"$nin": user_ids}}}})
            .modified_count,
        )

        # unset missing user from global folders
        print(
            "UNSET USER ON GLOBAL TOPICS",
            mongodb_database["topics"]
            .update_many({"user": {"$nin": user_ids}}, {"$set": {"user": None}})
            .modified_count,
        )

        # delete missing user folders
        print(
            "DELETE USER FOLDERS",
            mongodb_database["topic_folders"].delete_many({"user": {"$nin": user_ids, "$exists": True}}).deleted_count,
        )

    def backwards(self, mongodb_collection, mongodb_database):
        pass
