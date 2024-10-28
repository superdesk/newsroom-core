from superdesk.flask import render_template
from newsroom.gettext import get_session_locale
from newsroom.email import get_language_template_name


def init_app(app):
    app.add_template_global(render_search_tips_html)


async def render_search_tips_html(search_type) -> str:
    locale = (await get_session_locale() or "en").lower()
    template_name = get_language_template_name(f"search_tips_{search_type}", locale, "html")

    return await render_template(template_name)
