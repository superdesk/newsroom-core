import sys
import time
from pathlib import Path
from authlib.jose import jwt
from pytest import fixture
from newsroom.tests.conftest import drop_mongo, update_config, reset_elastic

root = (Path(__file__).parent / "..").resolve()
sys.path.insert(0, str(root))

AUTH_SECRET = "mgmt-api-test-secret"


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
    from quart import Config
    from newsroom.mgmt_api.factory import NewsroomMGMTAPI

    cfg = Config(root)
    cfg.from_object("newsroom.mgmt_api.default_settings")
    update_config(cfg)
    cfg["AUTH_SERVER_SHARED_SECRET"] = AUTH_SECRET
    drop_mongo(cfg)
    app = NewsroomMGMTAPI(config=cfg, testing=True)

    async with app.app_context():
        await reset_elastic(app)
        yield app


@fixture
def auth_headers():
    now = int(time.time())
    token = jwt.encode({"alg": "HS256"}, {"client_id": "test-client", "iat": now, "exp": now + 3600}, AUTH_SECRET)
    return {"Authorization": f"Bearer {token.decode()}"}
