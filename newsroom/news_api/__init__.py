from quart_babel import lazy_gettext


def init_app(app):
    if not app.config.get("NEWS_API_ENABLED"):
        return

    if hasattr(app, "section"):
        app.section("news_api", "News API", "api")

    app.general_setting(
        "news_api_time_limit_days",
        lazy_gettext("Time limit for News API products (in days)"),
        type="number",
        min=0,
        weight=500,
        description=lazy_gettext(
            "You can create an additional filter on top of the product definition. The time limit can be enabled for each company in the Permissions."
        ),  # noqa
        default=app.config.get("NEWS_API_TIME_LIMIT_DAYS", 0),
    )
