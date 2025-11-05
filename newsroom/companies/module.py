from typing import Any

from typing_extensions import TypedDict

from superdesk.core.app import SuperdeskAsyncApp
from superdesk.core.module import Module
from superdesk.core.web import EndpointGroup

from newsroom.core import NewshubModuleConfig
from .companies_async import company_resource_config


class CompanyTypeBase(TypedDict):
    id: str
    name: str


class CompanyType(CompanyTypeBase, total=False):
    wire_must: dict[str, Any]
    wire_must_not: dict[str, Any]


class CompanyConfigs(NewshubModuleConfig):
    company_types: list[CompanyType] = []


def init_module(app: SuperdeskAsyncApp):
    # Only set ``CLIENT_CONFIG.embed_permissions_enabled`` if this is the WebAPI
    if app.wsgi.config.get("CLIENT_CONFIG"):
        app.wsgi.config["CLIENT_CONFIG"]["embed_permissions_enabled"] = app.wsgi.config.get(
            "WIRE_EMBED_PERMISSIONS", True
        )

    if company_configs.register_endpoints:
        app.wsgi.register_endpoint(company_endpoints)


company_endpoints = EndpointGroup("companies", __name__)
company_configs = CompanyConfigs()
module = Module(
    name="newsroom.companies",
    config=company_configs,
    resources=[company_resource_config],
    endpoints=[],
    init=init_module,
)
