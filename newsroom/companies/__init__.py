import superdesk

from flask import Blueprint, current_app as newsroom_app, json
from flask_babel import lazy_gettext
from newsroom.auth import get_company
from newsroom.user_roles import UserRole
from .companies import CompaniesResource, CompaniesService
from apps.prepopulate.app_initialize import get_filepath

blueprint = Blueprint("companies", __name__)


def get_company_sections_monitoring_data(company_id, user):
    """get the section configured for the company"""
    if not company_id or user["user_type"] == UserRole.ADMINISTRATOR.value:
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


def load_countries_list():
    with open(get_filepath("vocabularies.json")) as f:
        data = json.load(f)
        countries = [
            {"value": item.get("qcode", ""), "text": item.get("name", "")}
            for cv in data
            if cv["_id"] == "countries"
            for item in cv["items"]
        ]
    countries.append({"value": "other", "text": "Other"})
    return countries


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

    # Populate countries data based on superdesk-core vocabularies.json file.
    with app.app_context():
        app.countries = load_countries_list()


from . import views  # noqa
