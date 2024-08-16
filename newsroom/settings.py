"""Settings UI module."""

import re
import copy

from quart_babel import gettext, lazy_gettext

from superdesk.core import get_current_app, get_app_config
from superdesk.flask import Blueprint, abort, render_template, g, jsonify
from superdesk.utc import utcnow

from newsroom.utils import get_json_or_400, set_version_creator
from newsroom.template_filters import newsroom_config
from newsroom.decorator import admin_only, account_manager_only
from inspect import iscoroutine


blueprint = Blueprint("settings", __name__)

GENERAL_SETTINGS_LOOKUP = {"_id": "general_settings"}


def get_settings_collection():
    return get_current_app().data.pymongo("items").db.settings


@blueprint.route("/settings/<app_id>")
@account_manager_only
async def app(app_id):
    from newsroom.users import get_user_profile_data  # noqa

    user_profile_data = await get_user_profile_data()
    app = get_current_app().as_any()

    for app in app.settings_apps:
        if app._id == app_id:
            value = app.data()
            data = await value if iscoroutine(value) else value
            return await render_template(
                "settings.html", setting_type=app_id, data=data, user_profile_data=user_profile_data
            )
    abort(404)


@blueprint.route("/settings/general_settings", methods=["POST"])
@admin_only
async def update_values():
    values = await get_json_or_400()

    error = validate_general_settings(values)
    if error:
        return "", error

    updates = {"values": values}
    set_version_creator(updates)
    updates["_updated"] = utcnow()

    get_settings_collection().update_one(GENERAL_SETTINGS_LOOKUP, {"$set": updates}, upsert=True)
    g.settings = None  # reset cache on update
    return jsonify(updates)


def get_initial_data(setting_key=None):
    data = get_setting(setting_key=setting_key, include_audit=True)
    return data


def get_setting(setting_key=None, include_audit=False):
    if not getattr(g, "settings", None):
        values = get_settings_collection().find_one(GENERAL_SETTINGS_LOOKUP)
        app = get_current_app().as_any()
        settings = copy.deepcopy(app._general_settings)
        if values:
            for key, val in values.get("values", {}).items():
                if not (val is None or val == "") and settings.get(key) is not None:
                    settings[key]["value"] = val
            if include_audit:
                settings["_updated"] = values.get("_updated")
                settings["version_creator"] = values.get("version_creator")

        g.settings = settings
    if setting_key:
        setting_dict = g.settings.get(setting_key) or {}
        return setting_dict.get("value", setting_dict.get("default"))
    return g.settings


def get_client_config():
    config = newsroom_config()
    for key, setting in (get_setting() or {}).items():
        if key not in ["_updated", "version_creator"]:
            value = setting.get("value", setting.get("default"))
            config["client_config"][key] = value

    # Copy certain app configs to client_config
    config["client_config"].update(
        dict(
            show_user_register=get_app_config("SHOW_USER_REGISTER") is True,
        )
    )
    return config


def validate_general_settings(values):
    # validate email formats for company_expiry_alert_recipients
    email_regex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    fields = [
        "company_expiry_alert_recipients",
        "coverage_request_recipients",
        "system_alerts_recipients",
        "product_seat_request_recipients",
    ]
    for field in fields:
        field_txt = (
            gettext("Company expiry alert recipients")
            if field == "company_expiry_alert_recipients"
            else gettext("Coverage request recipients")
        )

        for email in (values.get(field) or "").split(","):
            if email and not email_regex.match(email.strip()):
                return gettext("{}: Email IDs not in proper format".format(field_txt))


def init_app(app):
    app.settings_app(
        "general-settings",
        lazy_gettext("General Settings"),
        weight=800,
        data=get_initial_data,
    )
    app.add_template_global(get_setting)
    app.add_template_global(get_client_config)

    # basic settings
    app.general_setting(
        "google_analytics",
        lazy_gettext("Google Analytics ID"),
        default=app.config["GOOGLE_ANALYTICS"],
    )
    app.general_setting(
        "company_expiry_alert_recipients",
        lazy_gettext("Company expiry alert recipients"),
        description=lazy_gettext(
            "Comma separated list of email addresses to which the expiration alerts of companies will be sent to."
        ),
    )  # noqa
    app.general_setting(
        "coverage_request_recipients",
        lazy_gettext("Coverage request recipients"),
        description=lazy_gettext(
            "Comma separated list of email addresses who will receive the coverage request emails."
        ),
    )  # noqa
    app.general_setting(
        "system_alerts_recipients",
        lazy_gettext("System alerts recipients"),
        description=lazy_gettext("Comma separated list of email addresses who will receive system alerts."),
    )
    app.general_setting(
        "monitoring_report_logo_path",
        lazy_gettext("Monitoring report logo image"),
        description=lazy_gettext("Monitoring report logo image (jpg or png) for RTF reports."),
    )
    app.general_setting(
        "product_seat_request_recipients",
        lazy_gettext("Product Seat request recipients"),
        description=lazy_gettext("Comma separated list of email addresses who will receive product seat requests."),
    )
    app.general_setting(
        "allow_companies_to_manage_products",
        lazy_gettext("Allow companies to manage their own user product permissions"),
        description=lazy_gettext("Allow Company Admins to change section and product permissions for their users"),
        type="boolean",
        weight=500,
        default=app.config.get("DEFAULT_ALLOW_COMPANIES_TO_MANAGE_PRODUCTS"),
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
