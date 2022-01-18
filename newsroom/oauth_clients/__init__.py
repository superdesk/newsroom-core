import superdesk
from flask import Blueprint
from flask_babel import lazy_gettext
from .clients import ClientResource, ClientService

blueprint = Blueprint('oauth_clients', __name__)

from . import views   # noqa


def init_app(app):
    superdesk.register_resource('oauth_clients', ClientResource, ClientService, _app=app)
    app.settings_app('oauth_clients', lazy_gettext('OAuth Clients'), weight=100, data=views.get_settings_data,
                     allow_account_mgr=True)
