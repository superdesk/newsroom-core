from superdesk.flask import Blueprint, render_template
from newsroom.gettext import get_session_locale
from newsroom.email import get_language_template_name

blueprint = Blueprint("public", __name__)

from . import views  # noqa


def init_app(app):
    app.add_template_global(render_restricted_action_modal_body)


async def render_restricted_action_modal_body():
    locale = (await get_session_locale() or "en").lower()
    template_name = get_language_template_name("public_restricted_action_modal_body", locale, "html")

    return await render_template(template_name)
