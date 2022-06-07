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

import arrow
from bson import ObjectId
from celery import Celery
from celery.worker.request import Request
from kombu.serialization import register
from eve.io.mongo import MongoJSONEncoder
from eve.utils import str_to_date
from flask import json
from superdesk.celery_app import (  # noqa
    finish_subtask_from_progress,
    finish_task_for_progress,
    __get_redis,
    update_key,
    _update_subtask_progress
)

import newsroom


logger = logging.getLogger(__name__)
celery = Celery(__name__)
TaskBase = celery.Task


def try_cast(v):
    # False and 0 are getting converted to datetime by arrow
    if v is None or isinstance(v, bool) or v == 0:
        return v

    try:
        str_to_date(v)  # try if it matches format
        return arrow.get(v).datetime  # return timezone aware time
    except Exception:
        try:
            return ObjectId(v)
        except Exception:
            return v


def dumps(o):
    with newsroom.flask_app.app_context():
        return MongoJSONEncoder().encode(o)


def loads(s):
    o = json.loads(s)
    with newsroom.flask_app.app_context():
        return serialize(o)


def serialize(o):
    if isinstance(o, list):
        return [serialize(item) for item in o]
    elif isinstance(o, dict):
        if o.get('kwargs') and not isinstance(o['kwargs'], dict):
            o['kwargs'] = json.loads(o['kwargs'])
        return {k: serialize(v) for k, v in o.items()}
    else:
        return try_cast(o)


register('newsroom/json', dumps, loads, content_type='application/json')


def handle_exception(exc):
    """Log exception to logger."""
    logger.exception(exc)


class NewsroomRequest(Request):
    """
    Based on https://docs.celeryq.dev/en/stable/userguide/tasks.html#requests-and-custom-requests
    """

    def on_timeout(self, soft, timeout):
        super().on_timeout(soft, timeout)
        if not soft:
            logger.warning(
                'A hard timeout was enforced for task %s',
                self.task.name
            )

    def on_failure(self, exc_info, send_failed_event=True, return_ok=False):
        super().on_failure(
            exc_info,
            send_failed_event=send_failed_event,
            return_ok=return_ok
        )
        logger.warning(
            'Failure detected for task %s',
            self.task.name
        )


class AppContextTask(TaskBase):  # type: ignore
    abstract = True
    serializer = 'newsroom/json'
    Request = NewsroomRequest

    def __call__(self, *args, **kwargs):
        with newsroom.flask_app.app_context():
            try:
                return super().__call__(*args, **kwargs)
            except Exception as e:
                logger.warning('Error when calling task %s', self.task.name)
                handle_exception(e)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.warning('Failure detected for task %s', self.task.name)
        handle_exception(exc)


celery.Task = AppContextTask


def init_celery(app):
    celery.config_from_object(app.config, namespace='CELERY')
    app.celery = celery
    app.redis = __get_redis(app)
