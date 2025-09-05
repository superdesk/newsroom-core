from superdesk.core.tests.behave import setup_behave, BehaveTestFactory, BehaveContext
from superdesk.factory.app import SuperdeskApp

from newsroom.news_api.factory import get_app


class NewshubTestFactory(BehaveTestFactory):
    default_settings_module = "newsroom.news_api.default_settings"
    config = {
        "BEHAVE": True,
        "ELASTICSEARCH_FORCE_REFRESH": True,
        "NEWS_API_ENABLED": True,
        "NEWS_API_TIME_LIMIT_DAYS": 100,
        "SITE_NAME": "Newsroom",
        "CACHE_TYPE": "null",
        "ASYNC_AUTH_CLASS": "newsroom.news_api.api_tokens.auth:CompanyTokenAuth",
        "RATE_LIMIT_PERIOD": None,
        "RATE_LIMIT_REQUESTS": None,
    }
    auto_add_apps = False
    init_eve_resources = False
    init_request_context = False
    init_app_context = False

    async def get_app(self, config: dict) -> SuperdeskApp:
        return get_app(config=config, testing=True)

    async def before_test(self, context: BehaveContext) -> None:
        if not await super().before_test(context):
            return

        if "rate_limit" in context.scenario.tags:
            context.app.config["RATE_LIMIT_PERIOD"] = 300  # 5 minutes
            context.app.config["RATE_LIMIT_REQUESTS"] = 2

        context.headers = []


def before_all(context: BehaveContext):
    setup_behave(context, factory=NewshubTestFactory())
