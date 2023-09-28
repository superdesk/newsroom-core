import superdesk
from flask import Blueprint
from flask_babel import lazy_gettext

from . import products

blueprint = Blueprint("products", __name__)

from . import views  # noqa


def init_app(app):
    products.products_service = products.ProductsService("products", superdesk.get_backend())
    products.ProductsResource("products", app, products.products_service)
    app.settings_app("products", lazy_gettext("Products"), weight=400, data=views.get_settings_data)
