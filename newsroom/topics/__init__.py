from superdesk.core.module import Module

from .topics_async import topic_resource_config, topic_endpoints, init, get_user_topics  # noqa


module = Module(
    init=init,
    name="newsroom.topics",
    resources=[topic_resource_config],
    endpoints=[topic_endpoints],
)

from . import views  # noqa
