import sys
import time
from pathlib import Path
from authlib.jose import jwt
from pytest import fixture
from newsroom.tests.db import drop_mongo, reset_elastic
from newsroom.tests.app import get_test_config

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
    from newsroom.mgmt_api.factory import NewsroomMGMTAPI

    cfg = get_test_config(config_path="newsroom.mgmt_api.default_settings")
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
