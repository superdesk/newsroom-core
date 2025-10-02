from typing import Generator, Callable, TypeAlias, Awaitable
from inspect import isawaitable
import logging

import re
from lxml.html import HtmlElement
from lxml import html as lxml_html

from superdesk.flask import url_for
from superdesk.core import get_app_config
from superdesk.etree import to_string

from newsroom.types import SectionEnum, CompanyResource, EmbedPermissionUserAction
from newsroom.settings import get_setting
from newsroom.auth.utils import get_user_or_none_from_request, get_company_from_request
from newsroom.products import get_products_for_request_user_and_company

__all__ = [
    "iterate_embeds",
    "apply_company_permissions_to_embeds",
    "update_embeds_in_body",
    "update_embed_urls",
    "remove_all_embeds",
    "remove_internal_renditions",
    "set_association_links",
]
logger = logging.getLogger(__name__)


def iterate_embeds(
    root_elem: HtmlElement, embed_types: list[str] | None = None
) -> Generator[tuple[HtmlElement, str], None, None]:
    type_regex = r"\w+" if not embed_types else rf"(?:{'|'.join(embed_types)})"
    regex = re.compile(r" EMBED START " + type_regex + r" {id: \"editor_([0-9]+)")
    for comment in root_elem.xpath("//comment()"):
        m = regex.search(comment.text)
        if not m or not m.group(1):
            continue

        # if we've found an Embed Start comment, yield it now
        yield comment, f"editor_{m.group(1)}"


async def apply_company_permissions_to_embeds(
    items: list[dict], section: SectionEnum, use_download_as_view_permission: bool = False
) -> None:
    if not len(items) or not get_app_config("WIRE_EMBED_PERMISSIONS", True):
        return

    user = get_user_or_none_from_request(None)
    company = get_company_from_request(None)

    if (user and user.is_admin()) or not company:
        # If the current user is an admin, then there are no permissions to be applied
        return

    sdesk_products: set[str] = {
        product.sd_product_id
        for product in await get_products_for_request_user_and_company(section)
        if product.sd_product_id and product.is_enabled
    }

    for doc in items:
        _remove_or_disable_item_media(doc, company, sdesk_products, use_download_as_view_permission)


def _get_html_from_string(html_string: bytes | str | None) -> HtmlElement:
    # Fix a parsing issue when the HTML string starts with an embed comment
    # otherwise ``xpath("//comment()")[0].getparent()`` returns None
    # instead of the root element

    if not html_string:
        html_string = "<p></p>"
    elif isinstance(html_string, bytes) and html_string.startswith(b"<!-- EMBED START"):
        html_string = b"<p></p>" + html_string
    elif isinstance(html_string, str) and html_string.startswith("<!-- EMBED START"):
        html_string = "<p></p>" + html_string

    return lxml_html.fromstring(html_string)


EmbedUpdateCallback: TypeAlias = Callable[[dict, lxml_html.HtmlElement, str], bool]
EmbedUpdateAsyncCallback: TypeAlias = Callable[[dict, lxml_html.HtmlElement, str], Awaitable[bool]]


async def update_embeds_in_body(
    item,
    update_image_cb: EmbedUpdateCallback | EmbedUpdateAsyncCallback | None = None,
    update_audio_cb: EmbedUpdateCallback | EmbedUpdateAsyncCallback | None = None,
    update_video_cb: EmbedUpdateCallback | EmbedUpdateAsyncCallback | None = None,
):
    """
    Scans the story body for editor3 embeds and calls the appropriate passed function for each embed type.
    The functions should expect the item, element and the number associated with the association

    :param item:
    :param update_image_cb:
    :param update_audio_cb:
    :param update_video_cb:
    :return:
    """

    body_updated = False
    root_elem = _get_html_from_string(item.get("body_html"))
    for comment, editor_id in iterate_embeds(root_elem, ["Image", "Video", "Audio"]):
        # Assumes the sibling of the Embed Image comment is the figure tag containing the image
        embed_item = (item.get("associations") or {}).get(editor_id) or {}
        figure_elem = comment.xpath("following-sibling::figure[1]")
        if not figure_elem:
            continue  # No figure element found after the comment
        figure_elem = figure_elem[0]
        if figure_elem is not None and figure_elem.tag == "figure":
            if update_image_cb is not None:
                elem = figure_elem.find("./img")
                if elem is not None:
                    image_updated = update_image_cb(embed_item, elem, editor_id)
                    if isawaitable(image_updated):
                        image_updated = await image_updated
                    if image_updated:
                        body_updated = True
                    continue

            if update_audio_cb is not None:
                elem = figure_elem.find("./audio")
                if elem is not None:
                    audio_updated = update_audio_cb(embed_item, elem, editor_id)
                    if isawaitable(audio_updated):
                        audio_updated = await audio_updated
                    if audio_updated:
                        body_updated = True
                    continue

            if update_video_cb is not None:
                elem = figure_elem.find("./video")
                if elem is not None:
                    video_updated = update_video_cb(embed_item, elem, editor_id)
                    if isawaitable(video_updated):
                        video_updated = await video_updated
                    if video_updated:
                        body_updated = True

    if body_updated:
        item["body_html"] = to_string(root_elem, method="html")


async def update_embed_urls(item: dict, token: str | None = None):
    """
    Update the urls in the embeds to the endpoint that allows logging of the item that the embed belongs to

    :param item:
    :param token:
    :return:
    """

    def update_embed(embed_item: dict, elem: HtmlElement, embed_id: str):
        rendition_map = {"audio": "original", "video": "original", "img": "16-9"}
        rendition = rendition_map.get(elem.tag)

        src = None
        if rendition:
            src = embed_item.get("renditions", {}).get(rendition)

        if src is None:
            return

        url_kwargs = {
            "asset_id": src.get("media"),
            "item_id": item.get("_id"),
            "_external": True,
        }

        # Determine the endpoint and add token if present
        if token:
            endpoint_name = "assets.download"
            url_kwargs["token"] = token
        else:
            endpoint_name = "assets.get_item"

        # Assign the generated URL to the element's 'src' attribute
        if src is not None and elem is not None:
            elem.attrib["src"] = url_for(endpoint_name, **url_kwargs)
            return True  # Return True if assignment happened
        return False  # Return False if src or elem was None

    await update_embeds_in_body(item, update_embed, update_embed, update_embed)


def remove_all_embeds(item: dict, remove_by_class: bool = True, remove_media_embeds: bool = True) -> bool:
    """
    Remove the all embeds from the body of the article, including any divs with the embed_block attribute
    :param item:
    :param remove_by_class: If true removes any divs that have the embed-block class, should remove such things as
    embedded tweets
    :param remove_media_embeds: Remove any figure tags if the passed value is true
    :return:
    """
    original_body_html = item.get("body_html")
    if not original_body_html:
        return False  # No body to process, so no changes made

    root_elem = _get_html_from_string(original_body_html)

    if remove_by_class:
        embed_blocks = root_elem.xpath('//div[contains(concat(" ", @class, " "), " embed-block ")]')
        if embed_blocks:
            for embed in embed_blocks:
                parent = embed.getparent()
                if parent is not None:
                    parent.remove(embed)

    if not remove_media_embeds:
        item["body_html"] = to_string(root_elem, encoding="unicode", method="html")
        return True

    # clean all the embedded figures from the html, it will remove the comments as well
    cleaner = lxml_html.clean.Cleaner(add_nofollow=False, kill_tags=["figure"])
    cleaned_xhtml = cleaner.clean_html(root_elem)

    # remove the associations relating to the embeds
    kill_keys = [key for key in (item.get("associations") or {}) if key.startswith("editor_")]
    for key in kill_keys:
        item.get("associations", {}).pop(key, None)

    item["body_html"] = to_string(cleaned_xhtml, encoding="unicode", method="html")
    return True


def remove_internal_renditions(item: dict, remove_media: bool = False) -> dict:
    """
    Remove the internal and original image renditions from the feature media and embedded media. The media can
    optionally be removed as we do not serve this on the api.
    :param item:
    :param remove_media:
    :return:
    """
    allowed_renditions_setting = get_setting("news_api_allowed_renditions")
    if not allowed_renditions_setting:
        return item

    allowed_pic_renditions: set[str] = set(s.strip() for s in allowed_renditions_setting.split(",") if s.strip())

    for association_key, association_item in (item.get("associations") or {}).items():
        if not association_item:
            continue
        clean_renditions: dict = dict()
        for key, rendition in association_item.get("renditions", {}).items():
            if association_item.get("type") == "picture":
                if key in allowed_pic_renditions:
                    if remove_media:
                        rendition.pop("media", None)
                    clean_renditions[key] = rendition
            else:
                clean_renditions[key] = rendition

        item["associations"][association_key]["renditions"] = clean_renditions

        if isinstance(association_item, dict):
            association_item.pop("products", None)
            association_item.pop("subscribers", None)

    return item


def set_association_links(item: dict) -> None:
    """
    Updates the links in the associations to the endpoint that logs the download

    :param item:
    :return:
    """
    if not get_app_config("WIRE_EMBED_PERMISSIONS"):
        return

    for key, ass in (item.get("associations") or {}).items():
        if isinstance(ass, dict) and not key == "featuremedia":
            for rendition in ass.get("renditions", {}):
                if ass.get("renditions", {}).get(rendition, {}).get("href"):
                    ass.get("renditions", {}).get(rendition, {})["href"] = (
                        ass.get("renditions", {}).get(rendition, {}).get("href") + "?item_id=" + item.get("_id")
                    )


def _embed_item_has_product_code(embed_item: dict, products: set[str]) -> bool:
    embed_products: set[str] = {p["code"] for p in embed_item.get("products", []) if p.get("code")}
    return bool(embed_products & products)


def _get_associations_to_remove_or_disable(
    item: dict,
    company: CompanyResource,
    permitted_products: set[str],
) -> tuple[set[str], set[str]]:
    disable_display: set[str] = set()
    disable_download: set[str] = set()

    check_product_display = company.is_permissioned_for_embed("sd_product", EmbedPermissionUserAction.DISPLAY, False)

    for key, embed_item in (item.get("associations") or {}).items():
        if not (key and embed_item and (key.startswith("editor_") or key == "featuremedia")):
            continue

        embed_has_products = _embed_item_has_product_code(embed_item, permitted_products)
        content_type = embed_item.get("type", "picture")
        embed_type = key if key == "featuremedia" else content_type

        display_enabled = company.is_permissioned_for_embed(embed_type, EmbedPermissionUserAction.DISPLAY)
        if not display_enabled or (check_product_display and not embed_has_products):
            disable_display.add(key)
            # Item is not to be displayed, no need to check other user action permissions
            continue

        # This item has display enabled. Check to see if we need to disable the download from browser action
        elif content_type in {"audio", "video"} and not company.is_permissioned_for_embed(
            embed_type, EmbedPermissionUserAction.DOWNLOAD
        ):
            disable_download.add(key)

    return disable_display, disable_download


def _remove_or_disable_item_media(
    item: dict, company: CompanyResource, permitted_products: set[str], use_download_as_view_permission: bool = False
) -> None:
    disable_display, disable_download = _get_associations_to_remove_or_disable(item, company, permitted_products)
    if use_download_as_view_permission:
        disable_display |= disable_download
    disable_embed_codes = not company.is_permissioned_for_embed("embed_code", EmbedPermissionUserAction.DISPLAY)

    if not disable_download and not disable_display and not disable_embed_codes:
        return

    for key in disable_display:
        (item.get("associations") or {}).pop(key, None)

    if item.get("refs"):
        item["refs"] = [ref for ref in item["refs"] if ref.get("key") not in disable_display]

    if not item.get("associations"):
        item.pop("associations", None)

    html_updated: bool = False
    highlighted: bool = False
    root_elem: HtmlElement
    if item.get("es_highlight", {}).get("body_html", ""):
        root_elem = _get_html_from_string(item.get("es_highlight", {}).get("body_html", "")[0])
        highlighted = True
    else:
        root_elem = _get_html_from_string(item.get("body_html"))

    for comment, editor_id in iterate_embeds(root_elem):
        if editor_id in disable_display:
            parent = comment.getparent()
            for elem in comment.itersiblings():
                parent.remove(elem)
                if elem.text and " EMBED END " in elem.text:
                    break
            parent.remove(comment)
            html_updated = True
        else:
            figure = comment.getnext()
            for elem in figure.iterchildren():
                if elem.tag in ["video", "audio"]:
                    if editor_id in disable_download:
                        elem.attrib["data-disable-download"] = "true"
                if elem.text and " EMBED END " in elem.text:
                    break
            html_updated = True

    if disable_embed_codes:
        for embed_code_element in root_elem.xpath('//div[@class="embed-block"]'):
            embed_code_element.getparent().remove(embed_code_element)
            html_updated = True

    if html_updated:
        if highlighted:
            item["es_highlight"]["body_html"][0] = to_string(root_elem, method="html")
        else:
            item["body_html"] = to_string(root_elem, method="html")
