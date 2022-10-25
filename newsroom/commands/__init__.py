from .create_user import create_user  # noqa
from .elastic_rebuild import elastic_rebuild  # noqa
from .elastic_init import elastic_init  # noqa
from .content_reset import content_reset  # noqa
from .index_from_mongo import index_from_mongo, index_from_mongo_period  # noqa
from .remove_expired import remove_expired  # noqa
from .alerts import (  # noqa
    send_company_expiry_alerts,
    send_monitoring_schedule_alerts,
    send_monitoring_immediate_alerts,
)
from .data_updates import data_generate_update, data_upgrade, data_downgrade  # noqa
from .initialize_data import initialize_data  # noqa
from .schema_migrate import schema_migrate  # noqa
from .fix_topic_nested_filters import fix_topic_nested_filters  # noqa
from .remove_expired_agenda import remove_expired_agenda  # noqa

from newsroom.celery_app import celery


@celery.task(soft_time_limit=600)
def async_remove_expired_agenda():
    remove_expired_agenda()
