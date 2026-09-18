# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : Mark Pittaway
# Creation: 2025-04-29 10:10

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from superdesk.commands.data_updates import BaseDataUpdate


class DataUpdate(BaseDataUpdate):
    """Removes the ``locale`` field from users where the value is an empty string"""

    resource = "users"
    use_async_resources = True

    async def forwards(self, collection: AsyncIOMotorCollection, database: AsyncIOMotorDatabase) -> None:
        await collection.update_many({"locale": ""}, {"$unset": {"locale": 1}})

    async def backwards(self, collection: AsyncIOMotorCollection, database: AsyncIOMotorDatabase) -> None:
        pass
