from contextlib import contextmanager

import jinja2

from typing import Optional
from flask_babel import get_locale, get_timezone, _get_current_context, Locale, force_locale
import pytz

from superdesk.flask import g

TEMPLATE_LOCALE = "template_locale"


def set_template_locale(language: Optional[str] = None) -> None:
    setattr(g, TEMPLATE_LOCALE, language)


def get_template_locale() -> Optional[str]:
    return getattr(g, TEMPLATE_LOCALE, None)


def noop():
    return False


@contextmanager
def template_locale(locale: Optional[str] = None, timezone: Optional[str] = None):
    """Overriding babel locale and timezone using internals, but there is no public api for that."""
    ctx = _get_current_context()
    if not ctx:
        yield
        return

    old_locale = get_locale()
    old_tzinfo = get_timezone()

    if locale:
        ctx.babel_locale = Locale.parse(locale)
        set_template_locale(locale)

    if timezone:
        ctx.babel_tzinfo = pytz.timezone(timezone)

    with force_locale(locale):
        yield

    if locale:
        set_template_locale(None)
    if old_locale:
        ctx.babel_locale = old_locale
    if old_tzinfo:
        ctx.babel_tzinfo = old_tzinfo


class LocaleTemplateLoader(jinja2.FileSystemLoader):
    def get_source(self, environment: jinja2.Environment, template: str):
        source = None
        filename = None
        file_uptodate = noop
        template_locale = get_template_locale()

        if template_locale and f".{template_locale}." not in template:
            template_name, extension = template.rsplit(".", maxsplit=1)

            try:
                source, filename, file_uptodate = super().get_source(
                    environment, f"{template_name}.{template_locale}.{extension}"
                )
            except jinja2.TemplateNotFound:
                # no template for selected locale
                pass

        if not source:
            source, filename, file_uptodate = super().get_source(environment, template)

        def uptodate():
            """Must return False when locale changes to reload template."""
            return template_locale == get_template_locale() and file_uptodate()

        return source, filename, uptodate
