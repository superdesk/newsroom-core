from typing_extensions import TypedDict


class AdvancedSearchParams(TypedDict, total=False):
    all: str
    any: str
    exclude: str
    fields: list[str]
