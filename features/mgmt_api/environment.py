from superdesk.tests.environment import setup_before_all
from superdesk.tests.environment import before_feature, before_scenario  # noqa

from newsroom.auth_server.client import authorization
from newsroom.mgmt_api.app import get_app
from newsroom.tests.app import get_test_config


class TestClient:
    client_id = "test"


def before_all(context):
    config = get_test_config(
        {"BEHAVE": True, "MGMT_API_ENABLED": True},
        config_path="newsroom.mgmt_api.default_settings",
        test_name="behave"
    )
    setup_before_all(context, config, app_factory=get_app, before_test=before_test)


async def before_test(context, scenario):
    async with context.app.app_context():
        authorization.init_app(context.app, register_endpoint=False)
        token = authorization.generate_jwt_token(TestClient(), "client_credentials", "test", "")
        context.headers.append(("Authorization", f"Bearer {token}"))
