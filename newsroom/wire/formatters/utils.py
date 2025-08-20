from typing import Any, Set
from superdesk.core import get_app_config
from newsroom.assets import ASSETS_RESOURCE
from superdesk.flask import flask
from superdesk.etree import to_string
from newsroom.history_async import HistoryService
from newsroom.auth.utils import get_user_from_request, get_company_or_none_from_request
from newsroom.products import get_products_by_company_async
from newsroom.types import SectionEnum
from lxml import html as lxml_html
import re
import logging

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
            file = flask.current_app.media.get(
                associated_item.get("renditions").get(rendition).get("media"), ASSETS_RESOURCE
            )
            if not file:
                logger.warning("failed to get file for media {}".format(associated_item))
                continue
            zf.writestr(name, file.read())
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


async def remove_unpermissioned_embeds(item: dict[str, Any], section: SectionEnum = SectionEnum.WIRE):
    """
    :param item:
    :param section
    :return: The item with the embeds that the user is not allowed to download removed used by both the Newsoom API and
    any download formatters
    """

    if not get_app_config("EMBED_PRODUCT_FILTERING") and not get_app_config("NEWS_API_IMAGE_PERMISSIONS_ENABLED"):
        return

    company = get_company_or_none_from_request(None)

    if not company:
        logger.warning("Warning: No company found to determine embed permissions.")
        return

    # get the list of superdesk products that the company is permissioned for
    permitted_products: Set[str | None] = {
        p.sd_product_id
        for p in await get_products_by_company_async(company, product_type=section)
        if p.sd_product_id and p.is_enabled
    }

    embeds_to_remove_ids: Set[str] = set()

    current_associations = item.get("associations")
    if not isinstance(current_associations, dict):
        current_associations = {}

    for key, embed_data in current_associations.items():
        # get the list of products that the embedded item matched in superdesk
        if not embed_data:
            continue
        embed_products: Set[str] = {p.get("code") for p in embed_data.get("products", []) if p.get("code")}

        if not (embed_products & permitted_products):
            embeds_to_remove_ids.add(key)

    # Nothing to do
    if not embeds_to_remove_ids:
        return

    root_elem = lxml_html.fromstring(item.get("body_html", ""))
    regex = re.compile(r" EMBED START (?:Image|Video|Audio) {id: \"editor_([0-9]+)")
    html_updated = False
    comments = list(root_elem.xpath("//comment()"))
    for comment in comments:
        m = regex.search(comment.text)
        # if we've found an Embed Start comment
        if m and m.group(1):
            if "editor_" + m.group(1) in embeds_to_remove_ids:
                parent = comment.getparent()
                for elem in comment.itersiblings():
                    parent.remove(elem)
                    if elem.text and " EMBED END " in elem.text:
                        break
                parent.remove(comment)
                html_updated = True

    for key in embeds_to_remove_ids:
        item.get("associations", {}).pop(key, None)
        if "refs" in item:
            item["refs"] = [r for r in item.get("refs", []) if r["key"] != key]

    if not item.get("associations", {}):
        item.pop("associations", None)

    if html_updated:
        item["body_html"] = to_string(root_elem, method="html")
