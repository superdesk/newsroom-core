from typing import Any
import logging

from superdesk.flask import flask

from newsroom.auth.utils import get_user_from_request
from newsroom.assets.utils import get_media_file
from newsroom.history_async import HistoryService


logger = logging.getLogger(__name__)


async def add_media(zf, item: dict[str, Any]):
    """
    Add the media files associated with the item to the zip file
    :param zf: Zipfile
    :param item:
    :return:
    """
    added_files = []
    for _key, associated_item in item.get("associations", {}).items():
        if not associated_item:
            logger.warning("associated item missing for key {}".format(_key))
            continue
        for rendition in associated_item.get("renditions", []):
            name = associated_item.get("renditions").get(rendition).get("href").lstrip("/")
            if name in added_files:
                continue

            file = await get_media_file(associated_item.get("renditions").get(rendition).get("media"))
            if not file:
                logger.warning("failed to get file for media {}".format(associated_item))
                continue

            zf.writestr(name, await file.read())
            added_files.append(name)


async def log_media_downloads(item: dict[str, Any]) -> None:
    """
    Given an item create a download entry for all the associations, used by any download formatters that
    wish to report the media downloads
    :param item:
    :return:
    """
    for _key, associated_item in item.get("associations", {}).items():
        if not associated_item:
            continue
        action = "download " + associated_item.get("type")
        await HistoryService().create_media_history_record(
            item, _key, action, get_user_from_request(None), flask.request.args.get("type", "wire")
        )
