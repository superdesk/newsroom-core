from copy import deepcopy

from superdesk.tests import setup_notification, set_placeholder
from superdesk.tests.steps import get_prefixed_url
from superdesk.tests.environment import setup_before_all
from superdesk.tests.utils import set_use_eve

from newsroom.types import UserAuthResourceModel, CompanyResource, NavigationModel, ProductResourceModel
from newsroom.web.factory import get_app
from newsroom.agenda.filters import aggregations as agenda_aggs
from newsroom.tests.app import get_test_config, set_limiter_key_function
from tests.search import fixtures


orig_agenda_aggs = deepcopy(agenda_aggs)


def _get_app(*args, **kwargs):
    # Reset the Agenda aggregations config
    for key in list(agenda_aggs.keys()):
        agenda_aggs.pop(key)
    agenda_aggs.update(orig_agenda_aggs)

    app = get_app(*args, **kwargs)
    set_limiter_key_function()
    set_use_eve(app.async_app, False)

    return app


def before_all(context):
    config = get_test_config(
        {
            "BEHAVE": True,
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
        },
        test_name="behave"
    )
    setup_before_all(
        context,
        config,
        app_factory=_get_app,
        before_test=before_test,
    )


async def before_test(context, scenario):
    if scenario.status == "skipped":
        return

    if "notification" in scenario.tags:
        setup_notification(context)

    if "auth" in scenario.tags:
        await setup_users(context)
        await login_user(context, scenario)


async def setup_users(context):
    async with context.app.test_request_context("/login"):
        await NavigationModel.get_service().create(fixtures.NAVIGATIONS)
        await ProductResourceModel.get_service().create(fixtures.PRODUCTS)
        await CompanyResource.get_service().create(fixtures.COMPANIES)
        await UserAuthResourceModel.get_service().create(fixtures.USERS)


async def login_user(context, scenario):
    data = None

    if "admin" in scenario.tags:
        data = {
            "email": "admin2@sourcefabric.org",
            "password": "admin",
        }

    if data:
        url = "/login"

        response = await context.client.post(get_prefixed_url(context.app, url), form=data)
        assert response.status_code == 302, await response.get_data(as_text=True)

        # Get the logged-in user and add its ID to ``CONTEXT_USER_ID`` for use in behave tests
        user = await UserAuthResourceModel.get_service().find_one(email=data["email"])
        set_placeholder(context, "CONTEXT_USER_ID", str(user.id))
