from superdesk.core.resources import ResourceConfig, MongoResourceConfig, MongoIndexOptions

from content_api import MONGO_PREFIX

from .types import CompanyResource, CompanyProduct
from .service import CompanyService

__all__ = [
    "CompanyResource",
    "CompanyProduct",
    "CompanyService",
    "company_resource_config",
]


company_resource_config = ResourceConfig(
    name="companies",
    data_class=CompanyResource,
    service=CompanyService,
    mongo=MongoResourceConfig(
        prefix=MONGO_PREFIX,
        indexes=[
            MongoIndexOptions(
                name="name_1",
                keys=[("name", 1)],
                unique=True,
                collation={"locale": "en", "strength": 2},
            ),
            MongoIndexOptions(
                name="auth_domains_1",
                keys=[("auth_domains", 1)],
                unique=True,
                collation={"locale": "en", "strength": 2},
                partialFilterExpression={"auth_domains.0": {"$exists": True}},  # only check non empty
            ),
        ],
    ),
)
