from superdesk.core.module import Module

from .topics_async import (
    topic_resource_config,
    topic_endpoints,
    get_user_topics,
    get_agenda_notification_topics_for_query_by_id,
    get_topics_with_subscribers,
)
from . import topics

__all__ = [
    "get_user_topics",
    "topic_endpoints",
    "topic_resource_config",
    "get_agenda_notification_topics_for_query_by_id",
    "get_topics_with_subscribers",
]


def init_app(app):
    topics.TopicsResource("topics", app, topics.topics_service)


module = Module(
    name="newsroom.topics",
    resources=[topic_resource_config],
    endpoints=[topic_endpoints],
)

from . import views  # noqa
