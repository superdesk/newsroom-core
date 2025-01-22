from typing import Any, Optional, NoReturn
import re
import ipaddress

from bson import ObjectId
from bson.errors import InvalidId
from pydantic import AfterValidator, BeforeValidator, ValidationError
from pydantic_core import PydanticCustomError, InitErrorDetails
from quart_babel import gettext

from superdesk.core.app import get_current_async_app
from superdesk.core.resources import ResourceModel
from superdesk.core.resources.validators import AsyncValidator
from newsroom.core import get_current_wsgi_app


def validate_ip_address(error_string: str | None = None) -> AfterValidator:
    """Validates that the value is a valid IP address.

    :param error_string: An optional custom error string if validation fails
    """

    def _validate_ip_address(value: list[str] | str | None = None) -> list[str] | str | None:
        if value is None:
            return None
        elif isinstance(value, list):
            for address in value:
                _validate_ip_address(address)
        else:
            try:
                ipaddress.ip_network(value, strict=True)
            except ValueError as error:
                raise PydanticCustomError(
                    "ipaddress",
                    str(error_string) if error_string else gettext("Invalid IP address: {error}"),
                    dict(error=str(error)),
                )

        return value

    return AfterValidator(_validate_ip_address)


def validate_auth_provider(error_string: str | None = None) -> AfterValidator:
    """Validates that the value is a valid auth provider.

    :param error_string: An optional custom error string if validation fails
    """

    def _validate_provider(value: Optional[str] = None) -> Optional[str]:
        if not value:
            return None

        app = get_current_async_app()
        supported_provider_ids = [provider["_id"] for provider in app.wsgi.config["AUTH_PROVIDERS"]]
        if value not in supported_provider_ids:
            raise PydanticCustomError(
                "auth_provider",
                str(error_string) if error_string else gettext("Unknown auth provider {provider}"),
                dict(provider=value),
            )

        return value

    return AfterValidator(_validate_provider)


def validate_supported_dashboard(error_string: str | None = None) -> AfterValidator:
    """Validates that the dashboard is configured on the app

    :param error_string: An optional custom error string if validation fails
    """

    def _validate_dashboard_type_exists(value: str | None = None) -> str | None:
        if not value:
            return None

        app = get_current_wsgi_app()
        dashboard_ids = set((dashboard["_id"] for dashboard in app.dashboards))
        if value not in dashboard_ids:
            raise PydanticCustomError(
                "",
                str(error_string) if error_string else gettext("Dashboard type '{dashboard_id}' not found"),
                dict(dashboard_id=value),
            )

        return value

    return AfterValidator(_validate_dashboard_type_exists)


def validate_multi_field_iunique_value_async(
    resource_name: str, field_names: list[str], error_string: str | None = None
) -> AsyncValidator:
    """Validate that the combination of fields is unique in the resource (case-insensitive)

    :param resource_name: The name of the resource where the combination of fields must be unique
    :param field_names: The names of the fields to ensure unique combination
    :param error_string: An optional custom error string if validation fails
    """

    async def _validate_iunique_value(item: ResourceModel, value: Any) -> None:
        fields = {field: getattr(item, field) for field in field_names}
        if any(value is None for value in fields.values()):
            return

        app = get_current_async_app()
        resource_config = app.resources.get_config(resource_name)
        collection = app.mongo.get_collection_async(resource_config.name)

        query: dict[str, Any] = {"_id": {"$ne": item.id}}
        for field_name, value in fields.items():
            query[field_name] = re.compile("^{}$".format(re.escape(value.strip())), re.IGNORECASE)

        if await collection.find_one(query):
            raise PydanticCustomError(
                "unique",
                str(error_string) if error_string else gettext("Value in combination of fields must be unique"),
            )

    return AsyncValidator(_validate_iunique_value)


def validate_valid_objectid(field_name: str) -> BeforeValidator:
    """
    Creates a validator that processes a single value (str or ObjectId) for a specified field.
    It attempts to parse a string into `bson.ObjectId` if necessary and raises a validation error
    if the value is invalid or incompatible with `bson.ObjectId`.

    Args:
        field_name (str): The name of the field being validated, used in error messages.

    Returns:
        BeforeValidator: A validator that parses valid ObjectId strings and raises errors for invalid ones.

    Usage:
        This validator should be used with `typing.Annotated`, preferably placed to the most right side
        within the `Annotated` parameters list, to ensure it processes after other validators.
    """

    def _validate_objectid(value: str | ObjectId) -> ObjectId:
        if isinstance(value, str):
            try:
                value = ObjectId(value)
            except InvalidId:
                raise PydanticCustomError(
                    field_name, f"Provided ID '{value}' is not a valid ObjectId for field '{field_name}'."
                )
        elif not isinstance(value, ObjectId):
            raise PydanticCustomError(
                field_name,
                f"Wrong value type for ID '{value}' in field '{field_name}': expected 'str' or 'ObjectId'.",
            )

        return value

    return BeforeValidator(_validate_objectid)


def raise_custom_validation_error(resource: str, field_name: str, error_msg: str, input_value: Any) -> NoReturn:
    """Raise a Pydantic ValidationError so it is caught by our error handlers

    :raises pydantic.ValidationError: With the supplied details
    """

    raise ValidationError.from_exception_data(
        resource,
        [
            InitErrorDetails(
                type=PydanticCustomError(field_name, error_msg),
                loc=(field_name,),
                input=input_value,
            )
        ],
    )
