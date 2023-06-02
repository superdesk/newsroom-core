# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2023 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from bson import ObjectId
from flask import current_app as app

from superdesk import get_resource_service
from newsroom.types import User

USER_ADMIN_ID = ObjectId("445460066f6a58e1c6b11540")


def create_default_user() -> User:
    user_service = get_resource_service("users")
    user = user_service.find_one(req=None, _id=USER_ADMIN_ID)
    if not user:
        app.data.insert(
            "users",
            [
                {
                    "_id": USER_ADMIN_ID,
                    "first_name": "Admin",
                    "last_name": "Nistrator",
                    "email": "admin@nistrator.org",
                    "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                    "user_type": "administrator",
                    "is_validated": True,
                    "is_enabled": True,
                    "is_approved": True,
                    "sections": {"wire": True, "agenda": True},
                    "products": [],
                }
            ],
        )
        user = user_service.find_one(req=None, _id=USER_ADMIN_ID)

    return user
