from superdesk.core.tests.behave import setup_behave, BehaveTestFactory, BehaveContext
from superdesk.factory.app import SuperdeskApp

from newsroom.auth_server.client import authorization
from newsroom.mgmt_api.app import get_app


class TestClient:
    client_id = "test"


class ManagementAPITestFactory(BehaveTestFactory):
    default_settings_module = "newsroom.mgmt_api.default_settings"
    config = {
        "BEHAVE": True,
        "INSTALLED_APPS": [],
        "ELASTICSEARCH_FORCE_REFRESH": True,
        "MGMT_API_ENABLED": True,
        "CACHE_TYPE": "null",
        "AUTH_SERVER_SHARED_SECRET": "test-secret",
    }
    auto_add_apps = False
    init_eve_resources = False
    init_request_context = False
    init_app_context = False

    async def get_app(self, config: dict) -> SuperdeskApp:
        return get_app(config, testing=True)

    async def before_test(self, context: BehaveContext) -> None:
        await super().before_test(context)
        context.headers = [("Content-Type", "application/json"), ("Origin", "localhost")]
        async with context.app.app_context():
            token = authorization.generate_jwt_token(TestClient(), "client_credentials", "test", "")
            context.headers.append(("Authorization", f"Bearer {token}"))


def before_all(context: BehaveContext):
    setup_behave(context, ManagementAPITestFactory())
