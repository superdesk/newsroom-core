from copy import deepcopy

from superdesk.core import get_current_async_app, get_app_config
from superdesk.core.app import SuperdeskAsyncApp
from superdesk.core.mongo import MongoResourceConfig
from superdesk.flask import g

from content_api import MONGO_PREFIX

from newsroom.core import get_current_wsgi_app
from newsroom.template_filters import newsroom_config

GENERAL_SETTINGS_LOOKUP = {"_id": "general_settings"}


def register_resource(app: SuperdeskAsyncApp):
    app.mongo.register_resource_config("settings", MongoResourceConfig(prefix=MONGO_PREFIX))


def get_settings_collection():
    return get_current_async_app().mongo.get_collection("settings")


def get_setting(setting_key=None, include_audit=False):
    if not getattr(g, "settings", None):
        values = get_settings_collection().find_one(GENERAL_SETTINGS_LOOKUP)
        app = get_current_wsgi_app()
        settings = deepcopy(app._general_settings)
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


def update_settings_document(updates):
    get_settings_collection().update_one(GENERAL_SETTINGS_LOOKUP, {"$set": updates}, upsert=True)
