from flask import Config
from pytest import fixture

from newsroom.web.factory import get_app
from newsroom.tests.conftest import (  # noqa: F401
    drop_mongo,
    update_config,
    client,
    reset_elastic,
    root,
)


@fixture
def app():
    cfg = Config(root)
    cfg.from_object("newsroom.web.default_settings")
    cfg.from_object("tests.aap.settings")
    update_config(cfg)
    drop_mongo(cfg)
    app = get_app(config=cfg, testing=True)
    with app.app_context():
        reset_elastic(app)
        yield app
