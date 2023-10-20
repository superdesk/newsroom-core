import flask
import jinja2

from typing import Optional

TEMPLATE_LOCALE = "template_locale"


def set_template_locale(language: Optional[str] = None) -> None:
    setattr(flask.g, TEMPLATE_LOCALE, language)


def get_template_locale() -> Optional[str]:
    return getattr(flask.g, TEMPLATE_LOCALE, None)


def noop():
    return False


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
