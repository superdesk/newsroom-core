# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2023 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk
from .populate_resources import NewshubPopulateResourcesResource, NewshubPopulateResourcesService
from .app_init import AppInitResource, AppInitService


def init_app(app):
    service = AppInitService(AppInitResource.endpoint_name, backend=superdesk.get_backend())
    AppInitResource(AppInitResource.endpoint_name, app=app, service=service)
    superdesk.intrinsic_privilege(resource_name=AppInitResource.endpoint_name, method=["POST"])

    service = NewshubPopulateResourcesService(
        NewshubPopulateResourcesResource.endpoint_name, backend=superdesk.get_backend()
    )
    NewshubPopulateResourcesResource(NewshubPopulateResourcesResource.endpoint_name, app=app, service=service)
    superdesk.intrinsic_privilege(resource_name=NewshubPopulateResourcesResource.endpoint_name, method=["POST"])
