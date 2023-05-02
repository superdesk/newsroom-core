# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : marklark
# Creation: 2023-04-27 15:13

from eve.utils import config
from superdesk import get_resource_service
from superdesk.commands.data_updates import DataUpdate as _DataUpdate

from newsroom.companies.utils import get_company_section_names, get_company_product_ids


class DataUpdate(_DataUpdate):
    resource = "users"

    def forwards(self, mongodb_collection, _mongodb_database):
        companies = {company["_id"]: company for company in get_resource_service("companies").get(req=None, lookup={})}

        for user in mongodb_collection.find({}):
            company = companies.get(user.get("company"))
            updates = {}

            if isinstance(user.get("sections"), list):
                updates["sections"] = {name: True for name in user["sections"]}

            if company:
                company_section_names = get_company_section_names(company)
                company_product_ids = get_company_product_ids(company)
                user_sections = updates.get("sections") or user.get("sections") or {}

                updates = {
                    "sections": {
                        section: enabled and section in company_section_names
                        for section, enabled in user_sections.items()
                    },
                    "products": [
                        product
                        for product in user.get("products") or []
                        if product.get("section") in company_section_names and product.get("_id") in company_product_ids
                    ],
                }

            if updates:
                print(mongodb_collection.update({config.ID_FIELD: user.get(config.ID_FIELD)}, {"$set": updates}))

    def backwards(self, mongodb_collection, mongodb_database):
        pass
