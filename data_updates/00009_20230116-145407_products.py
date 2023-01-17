# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : petr
# Creation: 2023-01-16 14:54

from superdesk.commands.data_updates import DataUpdate as _DataUpdate


class DataUpdate(_DataUpdate):

    resource = "products"

    def forwards(self, mongodb_collection, mongodb_database):
        db = mongodb_database
        products = list(db.products.find({}))
        for company in db.companies.find({}):
            company_products = [
                {"_id": p["_id"], "section": p.get("product_type") or "wire"}
                for p in products
                if p.get("companies") and str(company["_id"]) in set(map(str, p["companies"]))
            ]
            db.companies.update_one({"_id": company["_id"]}, {"$set": {"products": company_products}})

    def backwards(self, mongodb_collection, mongodb_database):
        raise NotImplementedError()
