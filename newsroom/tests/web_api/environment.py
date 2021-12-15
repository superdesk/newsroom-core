from flask import json

from superdesk.tests import setup as setup_app
from superdesk.tests.environment import setup_before_all
from superdesk.tests.steps import get_prefixed_url

from newsroom.web.app import get_app
from newsroom.web.default_settings import CORE_APPS, BLUEPRINTS
from tests.search.fixtures import USERS, COMPANIES


def before_all(context):
    config = {
        'BEHAVE': True,
        'CORE_APPS': CORE_APPS,
        'BLUEPRINTS': BLUEPRINTS,
        'INSTALLED_APPS': [],
        'WTF_CSRF_ENABLED': False,
        'URL_PREFIX': '',
        'ELASTICSEARCH_FORCE_REFRESH': True,
        'SITE_NAME': 'Newsroom',
    }

    setup_before_all(context, config=config, app_factory=get_app)


def before_scenario(context, scenario):
    config = {
        'BEHAVE': True,
        'CORE_APPS': CORE_APPS,
        'BLUEPRINTS': BLUEPRINTS,
        'INSTALLED_APPS': [],
        'WTF_CSRF_ENABLED': False,
        'URL_PREFIX': '',
        'ELASTICSEARCH_FORCE_REFRESH': True,
        'SITE_NAME': 'Newsroom',
    }

    setup_app(context, config, app_factory=get_app, reset=True)
    context.headers = [("Content-Type", "application/json"), ("Origin", "localhost")]

    if scenario.status != "skipped":
        if "auth" in scenario.tags:
            setup_users(context)
            login_user(context, scenario)


def setup_users(context):
    with context.app.test_request_context():
        context.app.data.insert('companies', COMPANIES)
        context.app.data.insert('users', USERS)


def login_user(context, scenario):
    data = None

    if "admin" in scenario.tags:
        data = {
            'email': 'admin@sourcefabric.org',
            'password': 'admin'
        }

    if data:
        url = "/login"

        with context.app.test_request_context():
            context.client.post(
                get_prefixed_url(context.app, url),
                data=json.dumps(data),
                headers=context.headers,
                follow_redirects=True
            )
