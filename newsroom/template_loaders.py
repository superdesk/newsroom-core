from contextlib import contextmanager

import pytz
import jinja2

from typing import Optional
from quart_babel import get_timezone, force_locale
from quart_babel.utils import _get_current_context

from superdesk.flask import g

TEMPLATE_LOCALE = "template_locale"


def set_template_locale(language: Optional[str] = None) -> None:
    setattr(g, TEMPLATE_LOCALE, language)


def get_template_locale() -> Optional[str]:
    try:
        return getattr(g, TEMPLATE_LOCALE, None)
    except RuntimeError:
        return None


def noop():
    return False


@contextmanager
def template_locale(locale: Optional[str] = None, timezone: Optional[str] = None):
    """Overriding babel locale and timezone using internals, but there is no public api for that."""

    ctx = _get_current_context()

    if ctx is None or (locale is None and timezone is None):
        yield
        return

    old_tzinfo = get_timezone()

    try:
        if timezone:
            ctx.babel_tzinfo = pytz.timezone(timezone)
        if locale:
            set_template_locale(locale)
            with force_locale(locale):
                yield
        else:
            yield
    finally:
        if timezone:
            ctx.babel_tzinfo = old_tzinfo
        set_template_locale(None)


class LocaleTemplateLoader(jinja2.FileSystemLoader):
    def get_source(self, environment: jinja2.Environment, template: str):
        source = None
        filename = None
        file_uptodate = noop
        template_locale_str = get_template_locale()

        if template_locale_str and f".{template_locale_str}." not in template:
            template_name, extension = template.rsplit(".", maxsplit=1)

            try:
                source, filename, file_uptodate = super().get_source(
                    environment, f"{template_name}.{template_locale_str}.{extension}"
                )
            except jinja2.TemplateNotFound:
                # no template for selected locale
                pass

        if not source:
            source, filename, file_uptodate = super().get_source(environment, template)

        def uptodate():
            """Must return False when locale changes to reload template."""
            return template_locale_str == get_template_locale() and file_uptodate()

        return source, filename, uptodate
