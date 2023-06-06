# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2023 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from flask import current_app as app

from superdesk import get_resource_service
from newsroom import Resource, Service
from newsroom.auth.utils import start_user_session

from .utils import create_default_user


class NewshubPopulateResourcesResource(Resource):
    endpoint_name = "e2e_populate_resources"
    url = "e2e/populate_resources"
    resource_methods = ["POST"]
    public_methods = ["POST"]
    schema = {
        "resources": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "resource": {
                        "type": "string",
                        "required": True,
                    },
                    "use_resource_service": {
                        "type": "boolean",
                        "default": True,
                    },
                    "items": {
                        "type": "list",
                        "required": True,
                        "schema": {
                            "type": "dict",
                            "allow_unknown": True,
                        },
                    },
                },
            },
        },
    }


class NewshubPopulateResourcesService(Service):
    def create(self, docs, **kwargs):
        ids = []
        user = create_default_user()
        start_user_session(user, True)
        for doc in docs:
            for entry in doc.get("resources") or []:
                resource = entry.get("resource")
                items = entry.get("items") or []

                if entry.get("use_resource_service", True):
                    service = get_resource_service(resource)
                    for item in items:
                        app.data.mongo._mongotize(item, resource)
                        ids.extend(service.post([item]))
                else:
                    for item in items:
                        app.data.mongo._mongotize(item, resource)
                        ids.extend(app.data.insert(resource, [item]))

        return ids
