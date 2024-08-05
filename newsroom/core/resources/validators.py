from typing import Optional

import ipaddress
from pydantic import AfterValidator
from pydantic_core import PydanticCustomError
from flask_babel import gettext

from superdesk.core.app import get_current_async_app


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
