from quart import Config
from pytest import fixture

from superdesk.db import clean_dbs

from newsroom.web.factory import get_app
from newsroom.tests.conftest import update_config, client, root  # noqa: F401


@fixture
async def app():
    cfg = Config(root)
    cfg.from_object("newsroom.web.default_settings")
    cfg.from_object("tests.aap.settings")
    update_config(cfg)
    app = get_app(config=cfg, testing=True)
    async with app.app_context():
        await clean_dbs(app, init_indexes=True)
        yield app
