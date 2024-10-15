from newsroom import ELASTIC_PREFIX
import superdesk

from superdesk.core.app import SuperdeskAsyncApp
from superdesk.core.elastic import ElasticResourceConfig
from superdesk.core.module import Module
from superdesk.core.resources import ResourceConfig, ResourceModel

from .resource import NewsAPIFeedResource
from .service import NewsAPIFeedService
from .views import feed_endpoints


def init_app(app):
    superdesk.register_resource("news/feed", NewsAPIFeedResource, NewsAPIFeedService, _app=app)


def init_module(app: SuperdeskAsyncApp):
    class ItemsWrapperModel(ResourceModel):
        """Temporary model to wrap Items while items resource is ready"""

        pass

    app.resources.register(
        ResourceConfig(
            name="items",
            data_class=ItemsWrapperModel,
            elastic=ElasticResourceConfig(prefix=ELASTIC_PREFIX),
            default_sort=[("versioncreated", 1)],
        )
    )


module = Module(name="news.feed", init=init_module, endpoints=[feed_endpoints])
