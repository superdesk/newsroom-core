from flask_babel import lazy_gettext
import superdesk
from superdesk.flask import Blueprint

from .section_filters import SectionFiltersResource, SectionFiltersService

blueprint = Blueprint("section_filters", __name__)

from . import views  # noqa


def init_app(app):
    superdesk.register_resource("section_filters", SectionFiltersResource, SectionFiltersService, _app=app)
    app.settings_app(
        "section-filters",
        lazy_gettext("Section Filters"),
        weight=450,
        data=views.get_settings_data,
    )
