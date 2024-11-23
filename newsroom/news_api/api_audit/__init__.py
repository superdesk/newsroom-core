from superdesk.core.module import Module, SuperdeskAsyncApp
from superdesk.core.resources import ResourceConfig, MongoResourceConfig, ElasticResourceConfig

from newsroom import MONGO_PREFIX, ELASTIC_PREFIX
from newsroom.types import NewsApiAuditResourceModel


news_api_audit_resource_config = ResourceConfig(
    name="api_audit",
    data_class=NewsApiAuditResourceModel,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    elastic=ElasticResourceConfig(prefix=ELASTIC_PREFIX),
)


def init_app(app: SuperdeskAsyncApp) -> None:
    if app.wsgi.config.get("NEWS_API_ENABLED") and news_api_audit_resource_config not in module.resources:
        module.resources.append(news_api_audit_resource_config)


module = Module(
    "newsroom.news_api.api_audit",
    resources=[],
    init=init_app,
)
