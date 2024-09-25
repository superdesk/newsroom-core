from quart_babel import lazy_gettext

from superdesk.flask import Blueprint
import superdesk

from newsroom.monitoring import email_alerts  # noqa

from .monitoring import MonitoringResource, MonitoringService
from .search import MonitoringSearchResource, MonitoringSearchService
from .formatters.pdf_formatter import MonitoringPDFFormatter
from .formatters.rtf_formatter import MonitoringRTFFormatter
from .utils import get_keywords_in_text


blueprint = Blueprint("monitoring", __name__)

from . import views  # noqa


def init_app(app):
    superdesk.register_resource("monitoring", MonitoringResource, MonitoringService, _app=app)
    app.section("monitoring", app.config["MONITORING_SECTION"], "monitoring", "wire")
    app.settings_app(
        "monitoring",
        app.config["MONITORING_SECTION"],
        weight=200,
        data=views.get_settings_data,
        allow_account_mgr=True,
    )
    app.sidenav(app.config["MONITORING_SECTION"], "monitoring.index", "monitoring", section="monitoring")
    app.sidenav(
        app.config["SAVED_SECTION"],
        "monitoring.bookmarks",
        "bookmark",
        group=1,
        blueprint="monitoring",
        badge="saved-items-count",
    )

    app.download_formatter("monitoring_pdf", MonitoringPDFFormatter(), lazy_gettext("PDF"), ["monitoring"])
    app.download_formatter("monitoring_rtf", MonitoringRTFFormatter(), lazy_gettext("RTF"), ["monitoring"])

    superdesk.register_resource("monitoring_search", MonitoringSearchResource, MonitoringSearchService, _app=app)

    app.add_template_global(get_keywords_in_text, "get_keywords_in_text")

    # TODO-ASYNC: Removed in `develop` branch, investigate
    # theme_folder = getattr(app, "theme_folder", None) or path.join(app.config["SERVER_PATH"], "theme")
    # app.add_template_global(theme_folder, "monitoring_image_path")
