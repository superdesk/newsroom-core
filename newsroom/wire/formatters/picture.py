from typing import Any
import mimetypes
from quart_babel import lazy_gettext

from superdesk.core import get_app_config

from newsroom.types import SectionEnum
from newsroom.formatters import BaseFormatter, FormatterAssetType
from newsroom.wire.utils import get_picture


class PictureFormatter(BaseFormatter):
    format_id = "picture"
    name = lazy_gettext("Story Image")
    sections = [SectionEnum.WIRE]
    assets = [FormatterAssetType.PICTURE]

    MIMETYPE = "image/jpeg"
    MEDIATYPE = "picture"

    ALLOWED_EXTENSIONS = [".jpg", ".png"]

    def update_extension(self):
        extensions = mimetypes.guess_all_extensions(self.MIMETYPE, strict=True)
        for extension in extensions:
            if extension in self.ALLOWED_EXTENSIONS:
                return extension

        raise ValueError("Undefined extension")

    def get_picture_rendition(self, item: dict[str, Any], item_type: str | None = "items") -> tuple[str, str]:
        if item_type == "agenda":
            raise TypeError("Undefined format for agenda")

        picture = get_picture(item)

        if not picture:
            raise ValueError("Undefined picture")

        renditions = picture.get("renditions", {})
        picture_details = renditions.get(get_app_config("DOWNLOAD_RENDITION")) or renditions.get("baseImage", {})

        if picture_details is None:
            raise ValueError("Unable to find picture renditions")

        self.MIMETYPE = picture_details.get("mimetype", "image/jpeg")

        return picture_details["media"], self.update_extension()
