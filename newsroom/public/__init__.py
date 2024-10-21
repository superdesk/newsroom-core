from superdesk.core.app import SuperdeskAsyncApp
from superdesk.core.module import Module
from superdesk.flask import render_template
from newsroom.gettext import get_session_locale
from newsroom.email import get_language_template_name

from .views import public_endpoints


def init_module(app: SuperdeskAsyncApp):
    app.wsgi.add_template_global(render_restricted_action_modal_body)


module = Module(name="newsroom.public", init=init_module, endpoints=[public_endpoints])


async def render_restricted_action_modal_body():
    locale = (await get_session_locale() or "en").lower()
    template_name = get_language_template_name("public_restricted_action_modal_body", locale, "html")

    return await render_template(template_name)
