from typing import List, Dict

from werkzeug.utils import secure_filename
from flask import render_template, current_app as app

from newsroom.auth.utils import is_valid_session

from newsroom.types import DashboardCard, Article
from newsroom.public import blueprint
from newsroom.utils import query_resource
from newsroom.wire.items import get_items_for_dashboard
from newsroom.ui_config_async import UiConfigResourceService
from newsroom.users import get_user_profile_data

PUBLIC_DASHBOARD_CONFIG_CACHE_KEY = "public-dashboard-config"
PUBLIC_DASHBOARD_CARDS_CACHE_KEY = "public-dashboard-cards"
PUBLIC_DASHBOARD_ITEMS_CACHE_KEY = "public-dashboard-items"


async def get_public_dashboard_config():
    if app.cache.get(PUBLIC_DASHBOARD_CONFIG_CACHE_KEY):
        return app.cache.get(PUBLIC_DASHBOARD_CONFIG_CACHE_KEY)
    ui_config_service = UiConfigResourceService()

    config = await ui_config_service.get_section_config("home")
    app.cache.set(
        PUBLIC_DASHBOARD_CONFIG_CACHE_KEY, config, timeout=app.config.get("PUBLIC_CONTENT_CACHE_TIMEOUT", 240)
    )
    return config


def get_public_items_by_cards() -> Dict[str, List[Article]]:
    if app.cache.get(PUBLIC_DASHBOARD_ITEMS_CACHE_KEY):
        return app.cache.get(PUBLIC_DASHBOARD_ITEMS_CACHE_KEY)

    items_by_card = get_items_for_dashboard(get_public_cards(), True, True)
    app.cache.set(
        PUBLIC_DASHBOARD_ITEMS_CACHE_KEY, items_by_card, timeout=app.config.get("PUBLIC_CONTENT_CACHE_TIMEOUT", 240)
    )
    return items_by_card


def get_public_cards() -> List[DashboardCard]:
    if app.cache.get(PUBLIC_DASHBOARD_CARDS_CACHE_KEY):
        return app.cache.get(PUBLIC_DASHBOARD_CARDS_CACHE_KEY)

    cards = list(query_resource("cards", lookup={"dashboard": "newsroom"}))
    app.cache.set(PUBLIC_DASHBOARD_CARDS_CACHE_KEY, cards, timeout=app.config.get("PUBLIC_CONTENT_CACHE_TIMEOUT", 240))

    return cards


@blueprint.route("/page/<path:template>")
def page(template):
    return render_template("page-{template}.html".format(template=secure_filename(template)))


async def render_public_dashboard():
    user_profile_data = await get_user_profile_data()
    return render_template(
        "public_dashboard.html",
        data={
            "cards": get_public_cards(),
            "ui_config": await get_public_dashboard_config(),
            "items_by_card": get_public_items_by_cards(),
            "groups": app.config.get("WIRE_GROUPS", []),
        },
        user_profile_data=user_profile_data,
    )


@blueprint.route("/public/card_items")
def public_card_items():
    if not is_valid_session() and not app.config.get("PUBLIC_DASHBOARD"):
        return {"_items": []}
    return {"_items": get_public_items_by_cards()}
