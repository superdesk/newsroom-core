"""Settings UI module."""

from typing import cast
from quart_babel import lazy_gettext

from superdesk.core.module import Module, SuperdeskAsyncApp
from superdesk.core.config import ConfigModel

from .views import settings_endpoints
from .resource import register_resource, get_setting, get_client_config, get_settings_collection

GENERAL_SETTINGS_LOOKUP = {"_id": "general_settings"}

__all__ = [
    "get_settings_collection",
    "get_setting",
    "SettingsApp",
]


def get_initial_data(setting_key=None):
    data = get_setting(setting_key=setting_key, include_audit=True)
    return data


def init_app(app: SuperdeskAsyncApp):
    from newsroom.web.factory import NewsroomWebApp

    if settings_module_config.register_endpoints:
        app.wsgi.register_endpoint(settings_endpoints)

    register_resource(app)

    if settings_module_config.register_settings:
        newshub_app = cast(NewsroomWebApp, app.wsgi)
        newshub_app.settings_app(
            "general-settings",
            lazy_gettext("General Settings"),
            weight=800,
            data=get_initial_data,
        )
        newshub_app.add_template_global(get_setting)
        newshub_app.add_template_global(get_client_config)

        # basic settings
        newshub_app.general_setting(
            "google_analytics",
            lazy_gettext("Google Analytics ID"),
            default=app.wsgi.config["GOOGLE_ANALYTICS"],
        )
        newshub_app.general_setting(
            "company_expiry_alert_recipients",
            lazy_gettext("Company expiry alert recipients"),
            description=lazy_gettext(
                "Comma separated list of email addresses to which the expiration alerts of companies will be sent to."
            ),
        )  # noqa
        newshub_app.general_setting(
            "coverage_request_recipients",
            lazy_gettext("Coverage request recipients"),
            description=lazy_gettext(
                "Comma separated list of email addresses who will receive the coverage request emails."
            ),
        )  # noqa
        newshub_app.general_setting(
            "system_alerts_recipients",
            lazy_gettext("System alerts recipients"),
            description=lazy_gettext("Comma separated list of email addresses who will receive system alerts."),
        )
        newshub_app.general_setting(
            "monitoring_report_logo_path",
            lazy_gettext("Monitoring report logo image"),
            description=lazy_gettext("Monitoring report logo image (jpg or png) for RTF reports."),
        )
        newshub_app.general_setting(
            "product_seat_request_recipients",
            lazy_gettext("Product Seat request recipients"),
            description=lazy_gettext("Comma separated list of email addresses who will receive product seat requests."),
        )
        newshub_app.general_setting(
            "allow_companies_to_manage_products",
            lazy_gettext("Allow companies to manage their own user product permissions"),
            description=lazy_gettext("Allow Company Admins to change section and product permissions for their users"),
            type="boolean",
            weight=500,
            default=app.wsgi.config.get("DEFAULT_ALLOW_COMPANIES_TO_MANAGE_PRODUCTS"),
        )


class SettingsApp:
    def __init__(self, _id, name, weight=1000, data=None, allow_account_mgr=False):
        self._id = _id
        self.name = name
        self.weight = weight
        self.data = data if data is not None else self._default_data
        self.allow_account_mgr = allow_account_mgr

    def _default_data(self):
        return {}


class SettingsModuleConfig(ConfigModel):
    register_endpoints: bool = True
    register_settings: bool = True


settings_module_config = SettingsModuleConfig()
module = Module(
    name="newsroom.settings",
    init=init_app,
    config=settings_module_config,
    config_prefix="SETTINGS",
)
