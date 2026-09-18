from superdesk.core.module import Module
from superdesk.errors import SuperdeskApiError
from superdesk.core.resources import MongoResourceConfig, ResourceConfig, RestEndpointConfig

from newsroom import MONGO_PREFIX
from newsroom.types import TopicFolderResourceModel
from newsroom.topics_folders.folders import FolderResourceService
from newsroom.topics.topics_async import TopicResourceModel, TopicService


class GlobalTopicsService(TopicService):
    add_item_to_cache_on_create = True
    clear_item_cache_on_update = True

    async def on_create(self, docs: list[TopicResourceModel]) -> None:
        await super().on_create(docs)
        for doc in docs:
            user = doc.user
            if user:
                doc.original_creator = user
                doc.version_creator = user
            elif not doc.is_global:
                message = "Please set is_global True, or provide user in the body."
                raise SuperdeskApiError.badRequestError(message=message, payload=message)


topics_resource_config = ResourceConfig(
    name="topics",
    data_class=TopicResourceModel,
    service=GlobalTopicsService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    rest_endpoints=RestEndpointConfig(),
)

folders_resource_config = ResourceConfig(
    name="topic_folders",
    data_class=TopicFolderResourceModel,
    service=FolderResourceService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    rest_endpoints=RestEndpointConfig(),
)

module = Module(
    name="newsroom.mgmt_api.topics",
    resources=[topics_resource_config, folders_resource_config],
)
