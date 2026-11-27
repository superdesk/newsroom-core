from superdesk.tests.environment import setup_before_all
from superdesk.tests.utils import set_use_eve

from newsroom.news_api.factory import get_app
from newsroom.tests.app import get_test_config


def _get_app(config: dict):
    app = get_app(config)
    set_use_eve(app.async_app, False)
    return app


def before_all(context):
    config = get_test_config(
        {"BEHAVE": True, "NEWS_API_ENABLED": True, "NEWS_API_TIME_LIMIT_DAYS": 100},
        config_path="newsroom.news_api.default_settings",
        test_name="behave",
    )
    setup_before_all(context, config, app_factory=_get_app, before_test=before_test)


async def before_test(context, scenario):
    if "rate_limit" in scenario.tags:
        context.app.config["RATE_LIMIT_PERIOD"] = 300  # 5 minutes
        context.app.config["RATE_LIMIT_REQUESTS"] = 2
    else:
        context.app.config.pop("RATE_LIMIT_PERIOD", None)
        context.app.config.pop("RATE_LIMIT_REQUESTS", None)

    context.headers = []
