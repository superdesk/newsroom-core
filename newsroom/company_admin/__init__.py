from flask import Blueprint
from newsroom.web.factory import NewsroomWebApp

blueprint = Blueprint("company_admin", __name__)

from . import views  # noqa


def init_app(app: NewsroomWebApp):
    pass
