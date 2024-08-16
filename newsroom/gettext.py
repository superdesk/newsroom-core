from babel import core
from quart_babel import Babel, format_datetime, get_domain
from quart_babel.typing import ASGIRequest

from superdesk.core import get_app_config, get_current_app
from superdesk.flask import request, session
from newsroom.auth import get_user
from newsroom.template_loaders import get_template_locale
from newsroom.types import User


def get_client_translations(domain="client"):
    translations = get_domain().translations
    return {key: val for key, val in translations._catalog.items() if key and val}


def get_client_locales():
    client_locales = []

    for locale in get_app_config("LANGUAGES"):
        lang, *territory = locale.split("_")
        if len(territory) == 1:
            display_name = core.Locale(lang, territory=territory[0]).display_name.title()
        else:
            display_name = core.Locale(locale).display_name
        client_locales.append({"locale": locale, "name": display_name})

    return client_locales


async def get_session_locale(_req: ASGIRequest | None = None):
    try:
        if session.get("locale"):
            return session["locale"]
        user = get_user()
        if user and user.get("locale"):
            return user["locale"]
    except (RuntimeError, AttributeError, KeyError):
        pass

    default_language = get_app_config("DEFAULT_LANGUAGE")
    try:
        if request:
            languages = get_app_config("LANGUAGES")
            if request.args.get("language") and request.args.get("language") in languages:
                return request.args["language"]
            else:
                return request.accept_languages.best_match(languages, default_language)
    except AttributeError:
        pass

    return get_template_locale() or default_language


def get_user_timezone(user: User) -> str:
    try:
        return user["notification_schedule"]["timezone"]
    except (TypeError, ValueError, KeyError):
        pass
    return get_app_config("BABEL_DEFAULT_TIMEZONE") or get_app_config("DEFAULT_TIMEZONE")


async def get_session_timezone(_req: ASGIRequest | None = None):
    try:
        if session.get("timezone"):
            return session["timezone"]
        user = get_user()
        if user and user["notification_schedule"]["timezone"]:
            return user["notification_schedule"]["timezone"]
    except (RuntimeError, AttributeError, KeyError):
        pass

    try:
        app = get_current_app().as_any()
        if getattr(app, "session_timezone", None) is not None:
            return app.session_timezone
    except (AttributeError, RuntimeError):
        pass

    return get_app_config("BABEL_DEFAULT_TIMEZONE") or get_app_config("DEFAULT_TIMEZONE")


def set_session_timezone(timezone: str):
    try:
        session["timezone"] = timezone
    except RuntimeError:
        pass

    get_current_app().as_any().session_timezone = timezone


def clear_session_timezone():
    try:
        session.pop("timezone", None)
    except RuntimeError:
        pass

    get_current_app().config.pop("SESSION_TIMEZONE", None)


def setup_babel(app):
    Babel(
        app,
        locale_selector=get_session_locale,
        timezone_selector=get_session_timezone,
    )

    app.add_template_global(get_client_translations)
    app.add_template_global(get_client_locales)
    app.add_template_global(get_session_locale, "get_locale")
    app.add_template_global(format_datetime)
