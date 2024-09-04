# flake8 F401 "imported but unused" disabled in setup.cfg
from .create_user import create_user
from .elastic_rebuild import elastic_rebuild
from .elastic_init import elastic_init
from .content_reset import content_reset
from .index_from_mongo import index_from_mongo, index_from_mongo_period
from .remove_expired import remove_expired
from .alerts import (
    send_company_expiry_alerts,
    send_monitoring_schedule_alerts,
    send_monitoring_immediate_alerts,
)

from .data_updates import data_generate_update, data_upgrade, data_downgrade
from .initialize_data import initialize_data
from .schema_migrate import schema_migrate
from .fix_topic_nested_filters import fix_topic_nested_filters
from .remove_expired_agenda import remove_expired_agenda
from .scheduled_notifications import send_scheduled_notifications

from newsroom.celery_app import celery

from . import elastic_reindex
from .cli import commands_blueprint, newsroom_cli


@celery.task(soft_time_limit=600)
def async_remove_expired_agenda():
    remove_expired_agenda()
