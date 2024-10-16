from copy import deepcopy
import asyncio
import logging

from superdesk.flask import Config
from superdesk.tests.steps import get_prefixed_url
from newsroom.tests.conftest import drop_mongo, reset_elastic, root

from newsroom.web.factory import get_app
from newsroom.web.default_settings import CORE_APPS, BLUEPRINTS
from newsroom.agenda.agenda import aggregations as agenda_aggs
from tests.search.fixtures import USERS, COMPANIES


logger = logging.getLogger(__name__)
orig_agenda_aggs = deepcopy(agenda_aggs)


def before_all(context):
    pass


def before_scenario(context, scenario):
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(before_scenario_async(context, scenario))
    except Exception as e:
        # Make sure exceptions raised are printed to the console
        logger.exception(e)
        raise e


async def before_scenario_async(context, scenario):
    if "skip" in scenario.tags:
        scenario.skip("Marked with @skip")
        return

    for key in list(agenda_aggs.keys()):
        agenda_aggs.pop(key)
    agenda_aggs.update(orig_agenda_aggs)

    config = Config(
        root,
        {
            "BEHAVE": True,
            "TESTING": True,
            "CORE_APPS": CORE_APPS,
            "BLUEPRINTS": BLUEPRINTS,
            "INSTALLED_APPS": [],
            "WTF_CSRF_ENABLED": False,
            "URL_PREFIX": "",
            "ELASTICSEARCH_FORCE_REFRESH": True,
            "SITE_NAME": "Newsroom",
            "MONGO_URI": "mongodb://localhost/newsroom_behave",
            "CONTENTAPI_MONGO_URI": "mongodb://localhost/newsroom_behave",
            "MONGO_DBNAME": "newsroom_behave",
            "CONTENTAPI_MONGO_DBNAME": "newsroom_behave",
            "AUTH_SERVER_SHARED_SECRET": "2kZOf0VI9T70vU9uMlKLyc5GlabxVgl6",
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
    )

    drop_mongo(config)

    context.app = get_app(config=config, testing=True)
    async with context.app.app_context():
        await reset_elastic(context.app)

    context.headers = [("Content-Type", "application/json"), ("Origin", "localhost")]
    context.client = context.app.test_client()

    if scenario.status != "skipped":
        if "auth" in scenario.tags:
            await setup_users(context)
            await login_user(context, scenario)


async def setup_users(context):
    async with context.app.test_request_context("/login"):
        context.app.data.insert("companies", COMPANIES)
        context.app.data.insert("users", USERS)


async def login_user(context, scenario):
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
