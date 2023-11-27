# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : Mark Pittaway
# Creation: 2023-11-27 13:37

from bson import ObjectId
from superdesk.commands.data_updates import DataUpdate as _DataUpdate


class DataUpdate(_DataUpdate):
    resource = "topics"

    def forwards(self, mongodb_collection, mongodb_database):
        for topic in mongodb_collection.find({}):
            if not len(topic.get("subscribers") or []):
                continue

            update_required = False
            subscribers = []
            for subscriber in topic["subscribers"]:
                if isinstance(subscriber, dict):
                    # Subscriber already in the correct format (after scheduled notifications)
                    subscribers.append(subscriber)
                elif isinstance(subscriber, str) or isinstance(subscriber, ObjectId):
                    # Subscriber in previous format (before scheduled notifications)
                    subscribers.append({"user_id": ObjectId(subscriber), "notification_type": "real-time"})
                    update_required = True
                else:
                    print("Subscriber is in invalid format, skipping", subscriber)

            if update_required:
                mongodb_collection.update_one({"_id": topic["_id"]}, {"$set": {"subscribers": subscribers}})

    def backwards(self, mongodb_collection, mongodb_database):
        for topic in mongodb_collection.find({}):
            if not len(topic.get("subscribers") or []):
                continue

            subscribers = []
            for subscriber in topic["subscribers"]:
                if isinstance(subscriber, dict):
                    # Subscriber is in the correct format (after scheduled notifications)
                    subscribers.append(ObjectId(subscriber.get("user_id")))
                    # Subscriber in previous format (before scheduled notifications)
                elif isinstance(subscriber, str) or isinstance(subscriber, ObjectId):
                    subscribers.append(ObjectId(subscriber))
                else:
                    print("Subscriber is in invalid format, skipping", subscriber)

            mongodb_collection.update_one({"_id": topic["_id"]}, {"$set": {"subscribers": subscribers}})
