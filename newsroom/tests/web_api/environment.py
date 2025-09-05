from copy import deepcopy

from superdesk.core.tests.app import get_prefixed_url
from superdesk.core.tests.behave import setup_behave, BehaveContext, BehaveTestFactory, set_placeholder
from superdesk.factory.app import SuperdeskApp

from newsroom.types import UserAuthResourceModel, CompanyResource
from newsroom.web.factory import get_app
from newsroom.agenda.filters import aggregations as agenda_aggs

from tests.search.fixtures import USERS, COMPANIES


orig_agenda_aggs = deepcopy(agenda_aggs)


class NewshubTestFactory(BehaveTestFactory):
    default_settings_module = "newsroom.web.default_settings"
    config = {
        "BEHAVE": True,
        "WTF_CSRF_ENABLED": False,
        "URL_PREFIX": "",
        "AGENDA_GROUPS": [
            {
                "field": "sttdepartment",
                "label": "Department",
                "nested": {
                    "parent": "subject",
                    "field": "scheme",
                    "value": "sttdepartment",
                    "include_planning": True,
                },
            },
            {
                "field": "sttsubj",
                "label": "Subject",
                "nested": {
                    "parent": "subject",
                    "field": "scheme",
                    "value": "sttsubj",
                    "include_planning": True,
                },
            },
            {
                "field": "event_type",
                "label": "Event Type",
                "nested": {
                    "parent": "subject",
                    "field": "scheme",
                    "value": "event_type",
                },
            },
        ],
    }
    auto_add_apps = False
    init_eve_resources = False
    init_request_context = False
    init_app_context = False

    async def get_app(self, config: dict) -> SuperdeskApp:
        return get_app(config=config, testing=True)

    async def before_test(self, context: BehaveContext) -> None:
        if not await super().before_test(context):
            return

        if "auth" in context.scenario.tags:
            await setup_users(context)
            await login_user(context, context.scenario)


def before_all(context: BehaveContext):
    setup_behave(context, NewshubTestFactory())


async def setup_users(context: BehaveContext) -> None:
    async with context.app.test_request_context("/login"):
        await CompanyResource.get_service().create(COMPANIES)
        await UserAuthResourceModel.get_service().create(USERS)


async def login_user(context: BehaveContext, scenario):
    data = None

    if "admin" in scenario.tags:
        data = {
            "email": "admin2@sourcefabric.org",
            "password": "admin",
        }

    if data:
        url = "/login"

        response = await context.client.post(
            get_prefixed_url(context.app, url),
            form=data,
            headers=context.headers,
        )
        assert response.status_code == 302, response.status_code

        # Get the logged-in user and add its ID to ``CONTEXT_USER_ID`` for use in behave tests
        user = await UserAuthResourceModel.get_service().find_one(email=data["email"])
        set_placeholder(context, "CONTEXT_USER_ID", str(user.id))
