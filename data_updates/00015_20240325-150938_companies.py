# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : petr
# Creation: 2024-03-25 15:09

from superdesk.commands.data_updates import DataUpdate as _DataUpdate


class DataUpdate(_DataUpdate):
    resource = "companies"

    def forwards(self, mongodb_collection, mongodb_database):
        for company in mongodb_collection.find({"auth_domain": {"$exists": True}}):
            if company["auth_domain"]:
                print("Updating company", company["_id"])
                mongodb_collection.update_one(
                    {"_id": company["_id"]}, {"$set": {"auth_domains": [company["auth_domain"]]}}
                )

    def backwards(self, mongodb_collection, mongodb_database):
        for company in mongodb_collection.find({"auth_domains.0": {"$exists": True}}):
            mongodb_collection.update_one(
                {"_id": company["_id"]}, {"$set": {"auth_domain": [company["auth_domains"][0]]}}
            )
