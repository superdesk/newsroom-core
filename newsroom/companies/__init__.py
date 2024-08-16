import superdesk
from quart_babel import lazy_gettext

from newsroom.users.model import UserResourceModel

from superdesk.core import json, get_current_app
from apps.prepopulate.app_initialize import get_filepath

from newsroom.user_roles import UserRole

from .companies import CompaniesResource, CompaniesService
from .companies_async import CompanyService as CompanyServiceAsync, CompanyResource

from .module import module  # noqa

__all__ = [
    "CompanyServiceAsync",
    "CompanyResource",
]


async def get_company_sections_monitoring_data(company: CompanyResource, user: UserResourceModel):
    """get the section configured for the company"""
    app = get_current_app().as_any()

    if not company or user.user_type == UserRole.ADMINISTRATOR:
        return {"userSections": app.sections}

    data = {"monitoring_administrator": company.monitoring_administrator, "userSections": app.sections}

    if company and company.sections:
        data["userSections"] = [s for s in app.sections if company.sections.get(s["_id"])]

    return data


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
    app.settings_app(
        "companies",
        lazy_gettext("Company Management"),
        weight=100,
        data=views.get_settings_data,
        allow_account_mgr=True,
    )

    # Populate countries data based on superdesk-core vocabularies.json file.
    app.countries = load_countries_list()


from . import views  # noqa
