from newsroom.topics.topics_async import TopicResourceModel, TopicService
from newsroom.topics_folders.folders import FolderResourceService
from newsroom.types import TopicFolderResourceModel
from superdesk.errors import SuperdeskApiError
from newsroom.core import get_current_wsgi_app

from superdesk.core.resources import ResourceConfig, MongoResourceConfig, RestEndpointConfig
from content_api import MONGO_PREFIX
from superdesk.core.module import Module


class GlobalTopicsResource(TopicResourceModel):
    pass


class GlobalTopicsService(TopicService):
    async def on_create(self, docs):
        await super().on_create(docs)
        for doc in docs:
            user = doc.user
            if user:
                doc.original_creator = user
                doc.version_creator = user
            elif not doc.is_global:
                message = "Please set is_global True, or provide user in the body."
                raise SuperdeskApiError.badRequestError(message=message, payload=message)

    async def on_created(self, docs):
        await super().on_created(docs)
        app = get_current_wsgi_app()
        for doc in docs:
            app.cache.set(str(doc.id), doc)

    async def on_update(self, updates, original):
        await super().on_update(updates, original)
        app = get_current_wsgi_app()
        app.cache.delete(str(original.id))


topics_resource_config = ResourceConfig(
    name="topics",
    data_class=GlobalTopicsResource,
    service=GlobalTopicsService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    rest_endpoints=RestEndpointConfig(auth=False),
)

folders_resource_config = ResourceConfig(
    name="topic_folders",
    data_class=TopicFolderResourceModel,
    service=FolderResourceService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    rest_endpoints=RestEndpointConfig(auth=False),
)


module = Module(
    name="newsroom.mgmt_api.topics",
    resources=[topics_resource_config, folders_resource_config],
)
