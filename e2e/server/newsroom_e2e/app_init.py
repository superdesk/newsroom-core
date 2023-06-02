# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2023 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import multiprocessing

from flask import current_app as app

from superdesk.timer import timer

from newsroom import Resource, Service
from newsroom.tests.db import reset_elastic, drop_mongo
from .utils import create_default_user


class AppInitResource(Resource):
    endpoint_name = "e2e_init"
    url = "e2e/init"
    schema = {}
    resource_methods = ["POST"]
    public_methods = ["POST"]


class AppInitService(Service):
    def create(self, docs, **kwargs):
        with multiprocessing.Lock():
            with timer("app_init"):
                self._create()

            return ["OK"]

    def _create(self):
        reset_elastic()
        drop_mongo()
        app.init_indexes()
        app.data.init_elastic(app)
        create_default_user()
