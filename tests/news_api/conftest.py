import sys
from pathlib import Path
from pytest import fixture
from newsroom.tests.conftest import drop_mongo, update_config

root = (Path(__file__).parent / "..").resolve()
sys.path.insert(0, str(root))


@fixture
def init_agenda_items():
    pass


@fixture
def init_auth():
    pass


@fixture
def init_company():
    pass


@fixture
def init_items():
    pass


@fixture
def app():
    from flask import Config
    from newsroom.news_api.factory import NewsroomNewsAPI

    cfg = Config(root)
    cfg.from_object("newsroom.news_api.default_settings")
    update_config(cfg)
    drop_mongo(cfg)
    app = NewsroomNewsAPI(config=cfg, testing=True)
    with app.app_context():
        yield app
