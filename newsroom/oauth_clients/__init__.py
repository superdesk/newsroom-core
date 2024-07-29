from flask_babel import lazy_gettext

from superdesk.core.module import Module

from . import views  # noqa
from .clients_async import clients_model_config, clients_endpoints

module = Module(name="newsroom.oauth_clients", resources=[clients_model_config], endpoints=[clients_endpoints])


def init_app(app):
    app.settings_app(
        "oauth_clients",
        lazy_gettext("OAuth Clients"),
        weight=100,
        data=views.get_settings_data,
        allow_account_mgr=True,
    )
