import superdesk

from flask import Blueprint, current_app as newsroom_app
from flask_babel import lazy_gettext
from newsroom.auth import get_company
from .companies import CompaniesResource, CompaniesService

blueprint = Blueprint("companies", __name__)


def get_company_sections_monitoring_data(company_id):
    """get the section configured for the company"""
    if not company_id:
        return {"userSections": newsroom_app.sections}

    company = superdesk.get_resource_service("companies").find_one(req=None, _id=company_id)

    rv = {
        "monitoring_administrator": (company or {}).get("monitoring_administrator"),
        "userSections": newsroom_app.sections,
    }
    if company and company.get("sections"):
        rv["userSections"] = [s for s in newsroom_app.sections if company.get("sections").get(s["_id"])]

    return rv


def get_user_company_name(user) -> str:
    company = get_company(user)
    if company:
        return company.get("name", "")
    return ""


def init_app(app):
    superdesk.register_resource("companies", CompaniesResource, CompaniesService, _app=app)
    app.add_template_global(get_user_company_name)
    app.settings_app(
        "companies",
        lazy_gettext("Company Management"),
        weight=100,
        data=views.get_settings_data,
        allow_account_mgr=True,
    )


from . import views  # noqa
