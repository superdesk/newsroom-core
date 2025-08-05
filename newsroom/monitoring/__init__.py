from .service import MonitoringProfileService

__all__ = ["MonitoringProfileService"]


def init_app(app):
    # Import things inside this function to reduce circular imports
    from .utils import get_keywords_in_text
    from .views import get_settings_data

    app.section("monitoring", app.config["MONITORING_SECTION"], "monitoring", "wire")
    app.settings_app(
        "monitoring",
        app.config["MONITORING_SECTION"],
        weight=200,
        data=get_settings_data,
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

    app.add_template_global(get_keywords_in_text, "get_keywords_in_text")

    # TODO-ASYNC: Removed in `develop` branch, investigate
    # theme_folder = getattr(app, "theme_folder", None) or path.join(app.config["SERVER_PATH"], "theme")
    # app.add_template_global(theme_folder, "monitoring_image_path")
