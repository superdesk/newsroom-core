import os
from pathlib import Path
from pytest import fixture
from pymongo import MongoClient
from asgiref.wsgi import WsgiToAsgi

from newsroom.factory.app import BaseNewsroomApp
from superdesk.flask import Config, Flask
from superdesk.cache import cache
from newsroom.web.factory import get_app
from newsroom.tests import markers
from superdesk.tests.async_test_client import AsyncTestClient

root = (Path(__file__).parent / "..").resolve()


def update_config(conf):
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


def reset_elastic(app):
    indices = "%s*" % app.config["CONTENTAPI_ELASTICSEARCH_INDEX"]
    es = app.data.elastic.es
    es.indices.delete(indices, ignore=[404])
    with app.app_context():
        app.data.init_elastic(app)


def drop_mongo(config: Config):
    client: MongoClient = MongoClient(config["CONTENTAPI_MONGO_URI"])
    client.drop_database(config["CONTENTAPI_MONGO_DBNAME"])


@fixture
def app(request):
    cfg = Config(root)
    update_config(cfg)

    active_markers = [mark.name for mark in request.node.own_markers]

    if markers.enable_google_login.name in active_markers:
        cfg["FORCE_ENABLE_GOOGLE_OAUTH"] = True

    if markers.enable_saml.name in active_markers:
        cfg.setdefault("INSTALLED_APPS", []).append("newsroom.auth.saml")

    # drop mongodb now, indexes will be created during app init
    drop_mongo(cfg)

    app = get_app(config=cfg, testing=True)
    with app.app_context():
        reset_elastic(app)
        cache.clean()
        yield app


@fixture
async def app_async(app):
    app.async_app.elastic.init_all_indexes()
    yield app.async_app
    app.async_app.elastic.drop_indexes()
    await app.async_app.elastic.stop()
    app.async_app.stop()


@fixture
def client_async(app: BaseNewsroomApp, client):
    if client:
        print("*" * 100)
        pass

    asgi_app = WsgiToAsgi(app)
    client_async = AsyncTestClient(app, asgi_app)
    client_async.set_cookie("newsroom_session", client.get_cookie("newsroom_session").value)
    return client_async


@fixture
def client(app: Flask):
    return app.test_client()


@fixture
def runner(app: Flask):
    """Necessary fixture to invoke click commands from unit tests"""
    return app.test_cli_runner()
