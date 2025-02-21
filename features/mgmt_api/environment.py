import asyncio
from superdesk.tests.environment import setup_before_all, setup_before_scenario
from newsroom.auth_server.oauth2 import generate_jwt_token, config_oauth
from newsroom.mgmt_api.app import get_app as _get_app
from newsroom.mgmt_api.default_settings import CORE_APPS, MODULES, ASYNC_AUTH_CLASS, URL_PREFIX
from superdesk.tests import setup as setup_app
import logging

logger = logging.getLogger(__name__)


def get_app(*args, **kwargs):
    return _get_app(*args, **kwargs)


class TestClient:
    client_id = "test"


def before_all(context):
    config = {
        "BEHAVE": True,
        "CORE_APPS": CORE_APPS,
        "INSTALLED_APPS": [],
        "ELASTICSEARCH_FORCE_REFRESH": True,
        "MGMT_API_ENABLED": True,
        "CACHE_TYPE": "null",
        "MODULES": MODULES,
    }
    setup_before_all(context, config, app_factory=get_app)


def before_scenario(context, scenario):
    if "skip" in scenario.tags:
        scenario.skip("Marked with @skip")
        return

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(before_scenario_async(context, scenario))
    except Exception as e:
        # Make sure exceptions raised are printed to the console
        logger.exception(e)
        raise e


async def before_scenario_async(context, scenario):
    config = {
        "BEHAVE": True,
        "CORE_APPS": CORE_APPS,
        "MODULES": MODULES,
        "INSTALLED_APPS": [],
        "ELASTICSEARCH_FORCE_REFRESH": True,
        "MGMT_API_ENABLED": True,
        "AUTH_SERVER_SHARED_SECRET": "test-secret",
        "CACHE_TYPE": "null",
        "ASYNC_AUTH_CLASS": ASYNC_AUTH_CLASS,
        "URL_PREFIX": URL_PREFIX,
    }

    context.app = get_app(config=config)
    context.headers = []
    async with context.app.app_context():
        config_oauth(context.app)
        await setup_app(context, config, app_factory=get_app, reset=True)
        await setup_before_scenario(context, scenario, config, app_factory=get_app)
        token = generate_jwt_token(TestClient(), "client_credentials", "test", "")
        if isinstance(token, bytes):
            token = token.decode()
        context.headers.append(("Authorization", f"Bearer {token}"))
