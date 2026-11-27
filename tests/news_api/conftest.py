import sys
from pathlib import Path
from pytest import fixture
from newsroom.tests.db import drop_mongo, reset_elastic
from newsroom.tests.app import get_test_config

root = (Path(__file__).parent / "..").resolve()
sys.path.insert(0, str(root))


@fixture
async def init_agenda_items():
    pass


@fixture
async def init_auth():
    pass


@fixture
async def init_company():
    pass


@fixture
async def init_items():
    pass


@fixture
async def app():
    from newsroom.news_api.factory import NewsroomNewsAPI

    cfg = get_test_config(config_path="newsroom.news_api.default_settings")
    drop_mongo(cfg)
    app = NewsroomNewsAPI(config=cfg, testing=True)

    async with app.app_context():
        await reset_elastic(app)
        yield app
