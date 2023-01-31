from flask import Blueprint
from flask_babel import lazy_gettext

from newsroom.web.factory import NewsroomWebApp

blueprint = Blueprint("company_admin", __name__)

from . import views


def init_app(app: NewsroomWebApp):
    pass
