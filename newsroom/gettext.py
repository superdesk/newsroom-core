from babel import core
from flask import request, current_app, session
from flask_babel import Babel, get_translations, format_datetime

from newsroom.auth import get_user
from newsroom.template_loaders import get_template_locale
from newsroom.types import User


def get_client_translations(domain="client"):
    translations = get_translations()
    return {key: val for key, val in translations._catalog.items() if key and val}


def get_client_locales():
    client_locales = []

    for locale in current_app.config["LANGUAGES"]:
        lang, *territory = locale.split("_")
        if len(territory) == 1:
            display_name = core.Locale(lang, territory=territory[0]).display_name.title()
        else:
            display_name = core.Locale(locale).display_name
        client_locales.append({"locale": locale, "name": display_name})

    return client_locales


def get_session_locale():
    try:
        if session.get("locale"):
            return session["locale"]
        user = get_user()
        if user and user.get("locale"):
            return user["locale"]
    except RuntimeError:
        pass
    if request:
        if request.args.get("language") and request.args.get("language") in current_app.config["LANGUAGES"]:
            return request.args["language"]
        else:
            return request.accept_languages.best_match(
                current_app.config["LANGUAGES"], current_app.config["DEFAULT_LANGUAGE"]
            )
    if get_template_locale():
        return get_template_locale()
    return current_app.config["DEFAULT_LANGUAGE"]


def get_user_timezone(user: User) -> str:
    try:
        return user["notification_schedule"]["timezone"]
    except (TypeError, ValueError, KeyError):
        pass
    return current_app.config.get("BABEL_DEFAULT_TIMEZONE") or current_app.config["DEFAULT_TIMEZONE"]


def get_session_timezone():
    try:
        if session.get("timezone"):
            return session["timezone"]
        user = get_user()
        if user and user["notification_schedule"]["timezone"]:
            return user["notification_schedule"]["timezone"]
    except (RuntimeError, KeyError):
        pass

    try:
        if current_app.session_timezone is not None:
            return current_app.session_timezone
    except AttributeError:
        pass

    return current_app.config.get("BABEL_DEFAULT_TIMEZONE") or current_app.config["DEFAULT_TIMEZONE"]


def set_session_timezone(timezone: str):
    try:
        session["timezone"] = timezone
    except RuntimeError:
        pass

    current_app.session_timezone = timezone


def clear_session_timezone():
    try:
        session.pop("timezone", None)
    except RuntimeError:
        pass

    current_app.config.pop("SESSION_TIMEZONE", None)


def setup_babel(app):
    babel = Babel(app)

    babel.localeselector(get_session_locale)
    babel.timezoneselector(get_session_timezone)
    app.add_template_global(get_client_translations)
    app.add_template_global(get_client_locales)
    app.add_template_global(get_session_locale, "get_locale")
    app.add_template_global(format_datetime)
