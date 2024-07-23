from typing import Optional

import ipaddress
from pydantic import AfterValidator

from superdesk.core.app import get_current_async_app


def validate_ip_address() -> AfterValidator:
    """Validates that the value is a valid IP address."""

    def _validate_ip_address(value: Optional[str] = None) -> Optional[str]:
        if value is None:
            return None

        try:
            ipaddress.ip_network(value, strict=True)
        except ValueError as error:
            raise ValueError(f"Invalid IP address: {value}") from error

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
            raise ValueError(f"Unknown auth_provider '{value}' supplied")

        return value

    return AfterValidator(_validate_provider)
