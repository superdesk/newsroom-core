from typing import Any, TypedDict
from io import BytesIO
from enum import Enum, unique

import zipfile
from werkzeug.utils import secure_filename

from superdesk.errors import SuperdeskApiError
from superdesk.utc import utcnow

from newsroom.types import SectionEnum
from newsroom.utils import parse_dates


@unique
class FormatterAssetType(str, Enum):
    TEXT = "text"
    PICTURE = "picture"


class BaseFormatter:
    format_id: str
    name: str
    sections: list[SectionEnum]
    assets: list[FormatterAssetType] | None = None

    MIMETYPE = None
    BULK_MIMETYPE = "application/zip"
    FILE_EXTENSION = None
    MEDIATYPE = "text"
    MULTI = False
    MULTI_ZIP = False

    async def format_item(self, item: dict[str, Any], item_type: str | None = None) -> bytes:
        raise NotImplementedError()

    async def format_items(
        self, items: list[dict[str, Any]], item_type: str | None = None
    ) -> tuple[bytes | BytesIO, str | None]:
        items_file = BytesIO()
        with zipfile.ZipFile(items_file, mode="w") as zf:
            for item in items:
                parse_dates(item)  # fix for old items
                formatted_data = await self.format_item(item, item_type=item_type)
                zf.writestr(
                    secure_filename(self.format_filename(item)),
                    formatted_data,
                )

        items_file.seek(0)
        return items_file, None

    def format_filename(self, item: dict[str, Any] | None) -> str:
        assert self.FILE_EXTENSION
        _id = (item.get("slugline", item["_id"]) or item["_id"]).replace(" ", "-").lower()
        timestamp = item.get("versioncreated", item.get("_updated", utcnow()))
        return "{timestamp}-{_id}.{ext}".format(
            timestamp=timestamp.strftime("%Y%m%d%H%M"),
            _id=_id.lower(),
            ext=self.FILE_EXTENSION,
        )


_formatters: dict[str, type[BaseFormatter]] = {}


def register_formatter(formatter_class: type[BaseFormatter]):
    _formatters[formatter_class.format_id] = formatter_class


def get_formatter(format_id: str) -> BaseFormatter:
    try:
        return _formatters[format_id]()
    except KeyError:
        raise SuperdeskApiError.badRequestError(f"Failed to find registered formatter '{format_id}'")


def get_formatter_by_classname(classname: str) -> BaseFormatter:
    formatter_class = next((formatter for formatter in _formatters.values() if formatter.__name__ == classname), None)

    if formatter_class is None:
        raise SuperdeskApiError.badRequestError(f"Failed to find registered formatter '{classname}'")

    return formatter_class()


def get_formatters_for_section(section: SectionEnum) -> list[type[BaseFormatter]]:
    return [formatter_class for formatter_class in _formatters.values() if section in formatter_class.sections]


class FormatterIdAndName(TypedDict):
    format: str
    name: str
    types: list[SectionEnum]
    assets: list[FormatterAssetType]


def get_formatters_id_and_names(section: SectionEnum | None) -> list[FormatterIdAndName]:
    formatters = _formatters.values() if section is None else get_formatters_for_section(section)
    return [
        FormatterIdAndName(
            format=formatter.format_id,
            name=formatter.name,
            types=formatter.sections,
            assets=formatter.assets if formatter.assets is not None else [],
        )
        for formatter in formatters
    ]
