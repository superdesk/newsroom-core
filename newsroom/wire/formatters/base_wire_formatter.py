from lxml.html import HtmlElement

from superdesk.logging import logger

from newsroom.types import SectionEnum
from newsroom.formatters import BaseFormatter, FormatterAssetType
from newsroom.wire.embeds import (
    remove_internal_renditions,
    apply_company_permissions_to_embeds,
    update_embeds_in_body,
)


class BaseWireFormatter(BaseFormatter):
    assets = [FormatterAssetType.TEXT]

    def get_widest_rendition(self, association: dict) -> dict | None:
        widest: int = -1
        src_rendition: dict | None = None
        renditions: dict = association.get("renditions", {})
        for rendition in renditions.values():
            width = rendition.get("width", -2)

            if width > widest:
                widest = width
                src_rendition = rendition

        if src_rendition and widest > 0:
            return src_rendition

        logger.warning("href not found for the original in HTMLPackage formatter")
        return None

    def get_html_srcset_value_for_renditions(self, association: dict) -> str:
        """
        For the given marker (association) return the set of available hrefs and the widths
        :param association:
        :return:
        """

        srcset = []
        renditions: dict = association.get("renditions", {})
        for rendition in renditions.values():
            ref = rendition.get("href", "").lstrip("/")
            width = rendition.get("width", "")
            srcset.append(f"{ref} {width}w")

        return ",".join(srcset)

    async def update_image_element_attributes(self, embed_item: dict, elem: HtmlElement, embed_id: str) -> bool:
        elem.attrib["id"] = embed_id
        widest_rendition = self.get_widest_rendition(embed_item)
        if widest_rendition:
            elem.attrib["src"] = widest_rendition.get("href", "").lstrip("/")
        srcset = self.get_html_srcset_value_for_renditions(embed_item)
        if srcset:
            elem.attrib["srcset"] = srcset
            elem.attrib["sizes"] = "80vw"
        return True

    async def update_av_element_attributes(self, embed_item: dict, elem: HtmlElement, embed_id: str) -> bool:
        elem.attrib["id"] = embed_id

        try:
            elem.attrib["src"] = embed_item["renditions"]["original"]["href"].lstrip("/")
        except (KeyError, TypeError):
            logger.warning("audio/video href not found for the original in HTMLPackage formatter")

        elem.attrib.pop("alt", None)
        elem.attrib.pop("width", None)
        elem.attrib.pop("height", None)
        return True

    async def rewire_embdeded_images(self, item: dict) -> None:
        await update_embeds_in_body(
            item,
            self.update_image_element_attributes,
            self.update_av_element_attributes,
            self.update_av_element_attributes,
        )

    async def rewire_featuremedia(self, item: dict) -> None:
        """
        Set the references in the feature media strip the leading / to make it a legitimate relative path
        :param item:
        :return:
        """
        renditions = item.get("associations", {}).get("featuremedia", {}).get("renditions", {})
        for _rendition_key, rendition_data in renditions.items():
            rendition_data["href"] = rendition_data.get("href", "").lstrip("/")

    async def update_embeds(self, item: dict):
        await apply_company_permissions_to_embeds([item], SectionEnum.WIRE)

        # Remove the renditions we should not be showing the world
        remove_internal_renditions(item, remove_media=False)

        # set the references embedded in the html body of the story
        await self.rewire_embdeded_images(item)
        await self.rewire_featuremedia(item)
