import os
from pathlib import Path
from pytest import fixture

from bson import ObjectId
from quart import Quart, Config

from superdesk.cache import cache

from newsroom.web.factory import get_app
from newsroom.tests import markers
from newsroom.limiter import limiter

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
    return conf


def get_mongo_uri(key, dbname):
    """Read mongo uri from env variable and replace dbname.

    :param key: env variable name
    :param dbname: mongo db name to use
    """
    env_uri = os.environ.get(key, "mongodb://localhost/test")
    env_host = env_uri.rsplit("/", 1)[0]
    return "/".join([env_host, dbname])


@fixture
async def app(request):
    # Make sure old DB connections are closed
    prev_instance = getattr(app, "instance", None)
    if prev_instance:
        # Close all PyMongo Connections (new ones will be created with ``app_factory`` call)
        for key, val in prev_instance.extensions["pymongo"].items():
            val[0].close()

        prev_instance.async_app.stop()
        await prev_instance.async_app.elastic.stop()

    cfg = Config(root)
    update_config(cfg)

    active_markers = [mark.name for mark in request.node.own_markers]

    if markers.enable_google_login.name in active_markers:
        cfg["FORCE_ENABLE_GOOGLE_OAUTH"] = True

    if markers.enable_saml.name in active_markers:
        cfg.setdefault("INSTALLED_APPS", []).append("newsroom.auth.saml")

    # drop mongodb now, indexes will be created during app init
    drop_mongo(cfg)

    app_instance = get_app(config=cfg, testing=True)
    setattr(app, "instance", app_instance)
    limiter_key = str(ObjectId())

    async def limiter_key_function():
        return limiter_key

    limiter.key_function = limiter_key_function

    async with app_instance.app_context():
        await reset_elastic(app_instance)
        cache.clean()
        app_instance.init_indexes()
        yield app_instance

    # Clean up blueprints, so they can be re-registered
    import importlib

    for name in app_instance.config["BLUEPRINTS"]:
        mod = importlib.import_module(name)
        if getattr(mod, "blueprint"):
            mod.blueprint._got_registered_once = False


@fixture
def client(app: Quart):
    return app.test_client()


@fixture
def runner(app: Quart):
    """Necessary fixture to invoke click commands from unit tests"""
    return app.test_cli_runner()
