from typing import List, Dict

from werkzeug.utils import secure_filename
from flask import render_template, current_app as app

from superdesk import get_resource_service

from newsroom.types import DashboardCard, Article
from newsroom.public import blueprint
from newsroom.utils import query_resource
from newsroom.wire.items import get_items_for_dashboard

PUBLIC_DASHBOARD_CONFIG_CACHE_KEY = "public-dashboard-config"
PUBLIC_DASHBOARD_CARDS_CACHE_KEY = "public-dashboard-cards"
PUBLIC_DASHBOARD_ITEMS_CACHE_KEY = "public-dashboard-items"


def get_public_dashboard_config():
    if app.cache.get(PUBLIC_DASHBOARD_CONFIG_CACHE_KEY):
        return app.cache.get(PUBLIC_DASHBOARD_CONFIG_CACHE_KEY)

    config = get_resource_service("ui_config").get_section_config("home")
    app.cache.set(PUBLIC_DASHBOARD_CONFIG_CACHE_KEY, config, timeout=app.config.get("DASHBOARD_CACHE_TIMEOUT", 300))
    return config


def get_public_items_by_cards() -> Dict[str, List[Article]]:
    if app.cache.get(PUBLIC_DASHBOARD_ITEMS_CACHE_KEY):
        return app.cache.get(PUBLIC_DASHBOARD_ITEMS_CACHE_KEY)

    items_by_card = get_items_for_dashboard(get_public_cards(), True, True)
    app.cache.set(
        PUBLIC_DASHBOARD_ITEMS_CACHE_KEY, items_by_card, timeout=app.config.get("DASHBOARD_CACHE_TIMEOUT", 300)
    )
    return items_by_card


def get_public_cards() -> List[DashboardCard]:
    if app.cache.get(PUBLIC_DASHBOARD_CARDS_CACHE_KEY):
        return app.cache.get(PUBLIC_DASHBOARD_CARDS_CACHE_KEY)

    cards = list(query_resource("cards", lookup={"dashboard": "newsroom"}))
    app.cache.set(PUBLIC_DASHBOARD_CARDS_CACHE_KEY, cards, timeout=app.config.get("DASHBOARD_CACHE_TIMEOUT", 300))

    return cards


@blueprint.route("/page/<path:template>")
def page(template):
    return render_template("page-{template}.html".format(template=secure_filename(template)))


def render_public_dashboard():
    return render_template(
        "public_dashboard.html",
        data={
            "cards": get_public_cards(),
            "ui_config": get_public_dashboard_config(),
            "items_by_card": get_public_items_by_cards(),
            "groups": app.config.get("WIRE_GROUPS", []),
        },
    )


@blueprint.route("/public/card_items")
def public_card_items():
    return {"_items": get_public_items_by_cards()}
