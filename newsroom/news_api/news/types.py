import functools
from typing import Any, ClassVar
from typing_extensions import Self
from pydantic import Field, field_validator, model_validator

from content_api.errors import BadParameterValueError
from newsroom.search.types import BaseSearchRequestArgs


# set of fields that can be specified in the include_fields parameter
default_allowed_include_fields = {
    "type",
    "urgency",
    "priority",
    "language",
    "description_html",
    "located",
    "keywords",
    "source",
    "subject",
    "place",
    "wordcount",
    "charcount",
    "body_html",
    "readtime",
    "profile",
    "service",
    "genre",
    "associations",
    "headline",
    "extra",
}

# set of fields that are allowed to be excluded in the exclude_fields parameter
default_allowed_exclude_fields = {
    "version",
    "versioncreated",
    "firstcreated",
    "headline",
    "byline",
    "slugline",
}


class NewsApiSearchRequestArgs(BaseSearchRequestArgs):
    allowed_include_fields: ClassVar[set[str]] = default_allowed_include_fields

    allowed_exclude_fields: ClassVar[set[str]] = default_allowed_exclude_fields

    include_fields: list[str] | None = Field(
        default=None,
        description="Comma-separated list of fields to include",
    )

    exclude_fields: list[str] | None = Field(
        default=None,
        description="Comma-separated list of fields to exclude",
    )

    timezone: str | None = None

    # filter fields that will be applied in `filters.apply_filter_fields`
    service: str | None = None
    subject: str | None = None
    urgency: str | None = None
    priority: str | None = None
    genre: str | None = None
    item_source: str | None = None

    def to_dict(self, flatten_lists: bool = False, **kwargs):
        data = super().to_dict(**kwargs)

        # convert list attributes to comma-separated strings
        if flatten_lists:
            for key, value in data.items():
                if isinstance(value, list):
                    value = [str(v) for v in value]
                    data[key] = ",".join(value)
        return data

    @field_validator("include_fields", mode="before")
    @classmethod
    def validate_include_fields(cls, value: str | None) -> list[str] | None:
        return cls.validate_values_in_list(value, cls.allowed_include_fields, "include_fields")

    @field_validator("exclude_fields", mode="before")
    @classmethod
    def validate_exclude_fields(cls, value: str | None) -> list[str] | None:
        return cls.validate_values_in_list(value, cls.allowed_exclude_fields, "exclude_fields")

    @classmethod
    def validate_values_in_list(cls, value: str | None, allowed_list: set[str], field_name: str) -> list[str] | None:
        """
        Validates that all values in a comma-separated list are allowed.

        Args:
            value (str | None): Comma-separated string of values to validate.
            allowed_list (set[str]): Set of allowed values.
            field_name (str): Name of the field being validated, used in error messages.

        Returns:
            list[str]: List of validated values.

        Raises:
            BadParameterValueError: If any value is not allowed.
        """
        if value is None:
            return None

        strip_items = functools.partial(map, lambda s: s.strip())
        remove_empty = functools.partial(filter, None)  # type: ignore[var-annotated]

        fields = value.split(",")
        fields = set(remove_empty(strip_items(fields)))  # type: ignore[assignment]

        invalid_fields = [field for field in fields if field not in allowed_list]
        if invalid_fields:
            raise BadParameterValueError(f"`{field_name}` contains non-allowed values: {', '.join(invalid_fields)}")

        return fields

    @model_validator(mode="after")
    def check_include_exclude_fields_exclusivity(cls, values: Self) -> Any:
        """
        Validates that only one of `include_fields` or `exclude_fields` is provided.

        Raises:
            BadParameterValueError: If both `include_fields` and `exclude_fields` are provided.
        """

        if values.include_fields is not None and values.exclude_fields is not None:
            raise BadParameterValueError("Only one of `include_fields` or `exclude_fields` can be provided, not both.")

        return values
