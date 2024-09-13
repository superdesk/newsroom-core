import re
import ipaddress
from typing import Any, Mapping, Optional
from pydantic import AfterValidator
from pydantic_core import PydanticCustomError
from quart_babel import gettext

from superdesk.core.app import get_current_async_app
from superdesk.core.resources import ResourceModel
from superdesk.core.resources.validators import AsyncValidator
from newsroom.core import get_current_wsgi_app


def validate_ip_address() -> AfterValidator:
    """Validates that the value is a valid IP address."""

    def _validate_ip_address(value: Optional[str] = None) -> Optional[str]:
        if value is None:
            return None

        try:
            ipaddress.ip_network(value, strict=True)
        except ValueError:
            raise PydanticCustomError("ipaddress", gettext("Invalid IP address {ipaddress}"), dict(ipaddress=ipaddress))

        return value

    return AfterValidator(_validate_ip_address)


def validate_auth_provider() -> AfterValidator:
    """Validates that the value is a valid auth provider."""

    def _validate_provider(value: Optional[str] = None) -> Optional[str]:
        if not value:
            return None

        app = get_current_async_app()
        supported_provider_ids = [provider["_id"] for provider in app.wsgi.config["AUTH_PROVIDERS"]]
        if value not in supported_provider_ids:
            raise PydanticCustomError(
                "auth_provider", gettext("Unknown auth provider {provider}"), dict(provider=value)
            )

        return value

    return AfterValidator(_validate_provider)


def validate_supported_dashboard() -> AfterValidator:
    """Validates that the dashboard is configured on the app"""

    def _validate_dashboard_type_exists(value: str | None = None) -> str | None:
        if not value:
            return None

        app = get_current_wsgi_app()
        dashboard_ids = set((dashboard["_id"] for dashboard in app.dashboards))
        if value not in dashboard_ids:
            raise PydanticCustomError(
                "", gettext("Dashboard type '{dashboard_id}' not found"), dict(dashboard_id=value)
            )

        return value

    return AfterValidator(_validate_dashboard_type_exists)


def validate_multi_field_iunique_value_async(resource_name: str, field_names: list[str]) -> AsyncValidator:
    """Validate that the combination of fields is unique in the resource (case-insensitive)

    :param resource_name: The name of the resource where the combination of fields must be unique
    :param field_names: The names of the fields to ensure unique combination
    """

    async def _validate_iunique_value(item: ResourceModel, value: Any) -> None:
        fields = {field: getattr(item, field) for field in field_names}
        if any(value for value in fields.values()):
            return

        app = get_current_async_app()
        resource_config = app.resources.get_config(resource_name)
        collection = app.mongo.get_collection_async(resource_config.name)

        query: Mapping[str, Any] = {"_id": {"$ne": item.id}}
        for field_name, value in fields.items():
            query[field_name] = re.compile("^{}$".format(re.escape(value.strip())), re.IGNORECASE)

        if await collection.find_one(query):
            raise PydanticCustomError("unique", gettext("Value in combination of fields must be unique"))

    return AsyncValidator(_validate_iunique_value)
