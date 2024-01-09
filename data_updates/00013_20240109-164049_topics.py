# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : Mark Pittaway
# Creation: 2024-01-09 16:40

from superdesk.commands.data_updates import DataUpdate as _DataUpdate


class DataUpdate(_DataUpdate):
    resource = "topics"

    def forwards(self, mongodb_collection, mongodb_database):
        for topic in mongodb_collection.find({}):
            if not len((topic.get("filter") or {}).get("coverage_status") or []):
                continue

            topic["filter"]["coverage_status"] = [
                "not intended" if value == "not planned" else value for value in topic["filter"]["coverage_status"]
            ]
            mongodb_collection.update_one({"_id": topic["_id"]}, {"$set": {"filter": topic["filter"]}})

    def backwards(self, mongodb_collection, mongodb_database):
        for topic in mongodb_collection.find({}):
            if not len((topic.get("filter") or {}).get("coverage_status") or []):
                continue

            topic["filter"]["coverage_status"] = [
                "not planned" if value == "not intended" else value for value in topic["filter"]["coverage_status"]
            ]
            mongodb_collection.update_one({"_id": topic["_id"]}, {"$set": {"filter": topic["filter"]}})
