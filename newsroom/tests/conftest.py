import os
import pymongo
from flask import Config, Flask
from pathlib import Path
from pytest import fixture

from newsroom.web.factory import get_app
from newsroom.tests import markers

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
    client = pymongo.MongoClient(config["CONTENTAPI_MONGO_URI"])
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
        yield app


@fixture
def client(app: Flask):
    return app.test_client()
