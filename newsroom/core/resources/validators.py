from typing import Optional

import ipaddress
from pydantic import AfterValidator
from pydantic_core import PydanticCustomError
from quart_babel import gettext

from superdesk.core.app import get_current_async_app
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
