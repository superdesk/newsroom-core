# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : Ketan
# Creation: 2023-07-26

from superdesk.commands.data_updates import DataUpdate as _DataUpdate
from eve.utils import config


class DataUpdate(_DataUpdate):
    resource = "companies"

    def forwards(self, mongodb_collection, mongodb_database):
        for company in mongodb_collection.find({}):
            old_country_code = company.get("country")
            if old_country_code in ("au", "nz", "fin"):
                # Replace the old country code with the new qcode based on vocabularies
                if old_country_code == "au":
                    new_country_qcode = "AUS"
                elif old_country_code == "nz":
                    new_country_qcode = "NZL"
                elif old_country_code == "fin":
                    new_country_qcode = "FIN"

                print(
                    mongodb_collection.update(
                        {config.ID_FIELD: company.get(config.ID_FIELD)},
                        {"$set": {"country": new_country_qcode}},
                    )
                )

    def backwards(self, mongodb_collection, mongodb_database):
        pass
