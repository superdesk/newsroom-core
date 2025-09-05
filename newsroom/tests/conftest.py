import os
from pathlib import Path
from pytest import fixture
from copy import deepcopy

from bson import ObjectId
from quart import Quart, Config

from newsroom.web.factory import get_app
from newsroom.tests import markers
from newsroom.limiter import limiter
from superdesk.core.tests import TestAppContext
from superdesk.core.tests import app as test_app
from superdesk.core.tests.pytest_functions import PytestFunctionFactory, setup_pytest
from superdesk.factory.app import SuperdeskApp

from .db import reset_elastic, drop_mongo

root = (Path(__file__).parent / "..").resolve()


def use_config_file(file_path: str):
    setattr(update_config, "_config_path", file_path)


def update_config(conf):
    config_path = getattr(update_config, "_config_path", None)
    if config_path:
        conf.from_pyfile(config_path)

    conf["CONTENTAPI_URL"] = "http://localhost:5400"
    conf["ELASTICSEARCH_INDEX"] = conf["CONTENTAPI_ELASTICSEARCH_INDEX"] = "newsroom_test"
    conf["MONGO_DBNAME"] = conf["CONTENTAPI_MONGO_DBNAME"] = "newsroom_test"
    conf["MONGO_URI"] = conf["CONTENTAPI_MONGO_URI"] = "mongodb://localhost/newsroom_test"
    conf["SERVER_NAME"] = "localhost:5050"
    conf["WTF_CSRF_ENABLED"] = False
    conf["DEBUG"] = True
    conf["TESTING"] = True
    conf["WEBPACK_ASSETS_URL"] = None
    conf["BABEL_DEFAULT_TIMEZONE"] = "Europe/Prague"
    conf["DEFAULT_TIMEZONE"] = "Europe/Prague"
    conf["NEWS_API_ENABLED"] = True
    conf["AUTH_SERVER_SHARED_SECRET"] = "secret123"
    conf["SECRET_KEY"] = "foo"
    conf["CELERY_TASK_ALWAYS_EAGER"] = True
    conf["FORCE_ENABLE_GOOGLE_OAUTH"] = False
    conf["QUART_RATE_LIMITER_ENABLED"] = False
    conf["SAML_CLIENTS"] = []
    return conf


def get_mongo_uri(key, dbname):
    """Read mongo uri from env variable and replace dbname.

    :param key: env variable name
    :param dbname: mongo db name to use
    """
    env_uri = os.environ.get(key, "mongodb://localhost/test")
    env_host = env_uri.rsplit("/", 1)[0]
    return "/".join([env_host, dbname])


class NewshubTestAppFactory(PytestFunctionFactory):
    default_settings_module = "newsroom.web.default_settings"
    base_db_name = "nhub_test"
    auto_add_apps = False
    init_eve_resources = False
    init_app_context = False
    init_request_context = False

    async def get_app(self, config: dict) -> SuperdeskApp:
        return get_app(config=config, testing=True)

    async def before_module(self, context: TestAppContext) -> None:
        await super().before_module(context)
        limiter_key = str(ObjectId())

        async def limiter_key_function():
            return limiter_key

        limiter.key_function = limiter_key_function


@fixture(scope="session", autouse=True)
def app_session(context: TestAppContext) -> None:
    print("app_session")
    cfg = Config(root)
    update_config(cfg)

    app_factory = NewshubTestAppFactory()
    app_factory.config = cfg

    setup_pytest(context, app_factory)


@fixture(scope="function", autouse=True)
async def before_test(request, context: TestAppContext) -> Quart:
    active_markers = [mark.name for mark in request.node.own_markers]

    if markers.enable_google_login.name in active_markers:
        context.app.config["FORCE_ENABLE_GOOGLE_OAUTH"] = True

    if markers.enable_saml.name in active_markers:
        config = deepcopy(context.app.config)
        config.setdefault("INSTALLED_APPS", []).append("newsroom.auth.saml")
        app_instance = get_app(config=config, testing=True)
        context.app = app_instance
        context.async_app = app_instance.async_app
        context.app.test_client_class = test_app.TestClient
        context.client = context.app.test_client()

    async with context.app.app_context():
        yield context.app
