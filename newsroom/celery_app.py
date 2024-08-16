# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""
Created on May 29, 2014

@author: ioan
"""

import logging
import newsroom

from celery import Celery
from celery.worker.request import Request

from superdesk.celery_app import __get_redis, HybridAppContextTask, ContextAwareSerializerFactory


logger = logging.getLogger(__name__)


def get_newsroom_web_app():
    # using `newsroom.flas_app` as it's the one that returns the right app context
    return newsroom.flask_app


serializer_factory = ContextAwareSerializerFactory(get_newsroom_web_app)
serializer_factory.register_serializer("newsroom/json")


class NewsroomRequest(Request):
    """
    Based on https://docs.celeryq.dev/en/stable/userguide/tasks.html#requests-and-custom-requests
    """

    def on_timeout(self, soft, timeout):
        super().on_timeout(soft, timeout)
        if not soft:
            logger.warning("A hard timeout was enforced for task %s", self.task.name)

    def on_failure(self, exc_info, send_failed_event=True, return_ok=False):
        super().on_failure(exc_info, send_failed_event=send_failed_event, return_ok=return_ok)
        logger.warning("Failure detected for task %s", self.task.name)


class NewsroomContextTask(HybridAppContextTask):
    serializer = "newsroom/json"
    Request = NewsroomRequest

    def get_current_app(self):
        """Simple override to use the right context app"""
        return get_newsroom_web_app()


celery = Celery(__name__)
celery.Task = NewsroomContextTask


def init_celery(app):
    celery.config_from_object(app.config, namespace="CELERY")
    app.celery = celery
    app.redis = __get_redis(app)
