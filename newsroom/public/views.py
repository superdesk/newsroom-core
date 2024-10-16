from typing import List, Dict

from werkzeug.utils import secure_filename

from superdesk.core import get_current_app, get_app_config
from superdesk.flask import render_template

from newsroom.auth.utils import is_valid_session
from newsroom.types import Article, DashboardCardDict
from newsroom.public import blueprint
from newsroom.wire.items import get_items_for_dashboard
from newsroom.ui_config_async import UiConfigResourceService
from newsroom.users import get_user_profile_data
from newsroom.cards import CardsResourceService

PUBLIC_DASHBOARD_CONFIG_CACHE_KEY = "public-dashboard-config"
PUBLIC_DASHBOARD_CARDS_CACHE_KEY = "public-dashboard-cards"
PUBLIC_DASHBOARD_ITEMS_CACHE_KEY = "public-dashboard-items"


async def get_public_dashboard_config():
    app = get_current_app().as_any()
    if app.cache.get(PUBLIC_DASHBOARD_CONFIG_CACHE_KEY):
        return app.cache.get(PUBLIC_DASHBOARD_CONFIG_CACHE_KEY)
    ui_config_service = UiConfigResourceService()

    config = await ui_config_service.get_section_config("home")
    app.cache.set(
        PUBLIC_DASHBOARD_CONFIG_CACHE_KEY, config, timeout=get_app_config("PUBLIC_CONTENT_CACHE_TIMEOUT", 240)
    )
    return config


async def get_public_items_by_cards() -> Dict[str, List[Article]]:
    app = get_current_app().as_any()
    if app.cache.get(PUBLIC_DASHBOARD_ITEMS_CACHE_KEY):
        return app.cache.get(PUBLIC_DASHBOARD_ITEMS_CACHE_KEY)

    items_by_card = get_items_for_dashboard(await get_public_cards(), True, True)
    app.cache.set(
        PUBLIC_DASHBOARD_ITEMS_CACHE_KEY, items_by_card, timeout=get_app_config("PUBLIC_CONTENT_CACHE_TIMEOUT", 240)
    )
    return items_by_card


async def get_public_cards() -> List[DashboardCardDict]:
    app = get_current_app().as_any()
    if app.cache.get(PUBLIC_DASHBOARD_CARDS_CACHE_KEY):
        return app.cache.get(PUBLIC_DASHBOARD_CARDS_CACHE_KEY)

    cards = await (await CardsResourceService().find({"dashboard": "newsroom"})).to_list_raw()
    app.cache.set(PUBLIC_DASHBOARD_CARDS_CACHE_KEY, cards, timeout=get_app_config("PUBLIC_CONTENT_CACHE_TIMEOUT", 240))

    return cards


@blueprint.route("/page/<path:template>")
async def page(template):
    return await render_template("page-{template}.html".format(template=secure_filename(template)))


async def render_public_dashboard():
    user_profile_data = await get_user_profile_data()
    return await render_template(
        "public_dashboard.html",
        data={
            "cards": await get_public_cards(),
            "ui_config": await get_public_dashboard_config(),
            "items_by_card": await get_public_items_by_cards(),
            "groups": get_app_config("WIRE_GROUPS", []),
        },
        user_profile_data=user_profile_data,
    )


@blueprint.route("/public/card_items")
async def public_card_items():
    if not await is_valid_session() and not get_app_config("PUBLIC_DASHBOARD"):
        return {"_items": []}
    return {"_items": await get_public_items_by_cards()}
