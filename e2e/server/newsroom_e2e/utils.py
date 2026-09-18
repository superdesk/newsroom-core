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

from newsroom.types import UserResourceModel
from newsroom.users.service import UsersService
from tests.core.utils import create_entries_for

USER_ADMIN_ID = ObjectId("445460066f6a58e1c6b11540")


async def create_default_user() -> UserResourceModel:
    user = await UsersService().find_by_id(USER_ADMIN_ID)

    if not user:
        await create_entries_for(
            "auth_user",
            [
                {
                    "_id": USER_ADMIN_ID,
                    "first_name": "Admin",
                    "last_name": "Nistrator",
                    "email": "admin@example.com",
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
        user = await UsersService().find_by_id(USER_ADMIN_ID)

    return user
