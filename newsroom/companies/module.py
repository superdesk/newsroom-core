from typing import Any
from typing_extensions import TypedDict

from superdesk.core.config import ConfigModel
from superdesk.core.module import Module
from superdesk.core.web import EndpointGroup

from .companies_async import company_resource_config


class CompanyTypeBase(TypedDict):
    id: str
    name: str


class CompanyType(CompanyTypeBase, total=False):
    wire_must: dict[str, Any]
    wire_must_not: dict[str, Any]


class CompanyConfigs(ConfigModel):
    company_types: list[CompanyType] = []


company_endpoints = EndpointGroup("companies", __name__)
company_configs = CompanyConfigs()
module = Module(
    name="newsroom.companies",
    config=company_configs,
    resources=[company_resource_config],
    endpoints=[company_endpoints],
)
