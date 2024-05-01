import superdesk
from flask import Blueprint
from flask_babel import lazy_gettext

from newsroom.utils import url_for_agenda
from .agenda import AgendaResource, AgendaService, aggregations, PRIVATE_FIELDS
from newsroom.search.config import init_nested_aggregation
from .featured import FeaturedResource, FeaturedService
from . import formatters
from .utils import (
    get_coverage_email_text,
    get_coverage_content_type_name,
    get_coverage_publish_time,
    get_coverage_scheduled_date,
    get_planning_coverages,
    get_coverage_status,
)


blueprint = Blueprint("agenda", __name__)

from . import views  # noqa


def init_app(app):
    superdesk.register_resource("agenda", AgendaResource, AgendaService, _app=app)
    superdesk.register_resource("agenda_featured", FeaturedResource, FeaturedService, _app=app)

    app.section("agenda", app.config["AGENDA_SECTION"], "agenda")
    app.sidenav(app.config["AGENDA_SECTION"], "agenda.index", "calendar", section="agenda")
    app.sidenav(
        app.config["SAVED_SECTION"],
        "agenda.bookmarks",
        "bookmark",
        group=1,
        blueprint="agenda",
        badge="saved-items-count",
    )

    app.download_formatter("ical", formatters.iCalFormatter(), "iCalendar", ["agenda"])
    app.download_formatter("Csv", formatters.CSVFormatter(), "CSV", ["agenda"])
    app.add_template_global(url_for_agenda)
    app.add_template_global(get_coverage_email_text)
    app.add_template_global(get_coverage_content_type_name, "get_coverage_content_type")
    app.add_template_global(get_coverage_scheduled_date, "get_coverage_date")
    app.add_template_global(get_coverage_publish_time, "get_coverage_publish_time")
    app.add_template_global(get_planning_coverages)
    app.add_template_global(get_coverage_status, "get_coverage_status")
    app.general_setting(
        "google_maps_styles",
        lazy_gettext("Google Maps Styles"),
        default="",
        description=lazy_gettext(
            "Provide styles delimited by &(ampersand). For example, feature:poi|element:labels|visibility:off&transit|visibility:off. Refer to https://developers.google.com/maps/documentation/maps-static/styling for more details"
        ),  # noqa
        client_setting=True,
    )

    if app.config.get("AGENDA_GROUPS") is None:
        # Default values are applied if ``AGENDA_GROUPS`` is not defined or None
        app.config["AGENDA_GROUPS"] = [
            {
                "field": "service",
                "label": lazy_gettext("Category"),
            },
            {
                "field": "subject",
                "label": lazy_gettext("Subject"),
            },
            {
                "field": "urgency",
                "label": lazy_gettext("News Value"),
            },
            {
                "field": "place",
                "label": lazy_gettext("Place"),
            },
        ]

    init_nested_aggregation(AgendaResource, app.config.get("AGENDA_GROUPS", []), aggregations)

    if app.config.get("AGENDA_HIDE_COVERAGE_ASSIGNEES"):
        PRIVATE_FIELDS.extend(["*.assigned_desk_*", "*.assigned_user_*"])
