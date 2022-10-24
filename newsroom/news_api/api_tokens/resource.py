from copy import deepcopy

from content_api.tokens import CompanyTokenResource


class NewsApiTokensResource(CompanyTokenResource):
    internal_resource = True
    schema = deepcopy(CompanyTokenResource.schema)
    schema.update(
        {
            "enabled": {"type": "boolean", "default": True},
            "rate_limit_requests": {"type": "integer"},
            "rate_limit_expiry": {"type": "datetime"},
        }
    )
