import logging
from datetime import datetime, timedelta

from email.utils import format_datetime
from lxml import etree
from lxml.etree import Element, SubElement, QName, CDATA

from superdesk.core import get_app_config
from superdesk.core.types import Request, Response
from superdesk.core.utils import str_to_date
from superdesk.utc import utcnow
from superdesk.flask import url_for

from newsroom.types import SectionEnum
from newsroom.wire.formatters.utils import remove_unpermissioned_embeds
from newsroom.news_api.utils import update_embed_urls
from newsroom.news_api.news.search_service import NewsApiSearchServiceAsync

logger = logging.getLogger(__name__)


class RSSFormatter:
    name: str = "RSS Feed"
    mimetype: str = "application/rss+xml; charset=utf-8"
    nsmap: dict = {
        "dcterms": "http://purl.org/dc/terms/",
        "media": "http://search.yahoo.com/mrss/",
        "dc": "http://purl.org/dc/elements/1.1/",
        "mi": "http://schemas.ingestion.microsoft.com/common/",
        "content": "http://purl.org/rss/1.0/modules/content/",
    }
    item_field: str = "item"
    item_id_field: str = "guid"

    async def format_feed(self, token: str | None, request: Request) -> Response:
        XML_ROOT = '<?xml version="1.0" encoding="UTF-8"?>'
        feed, channel = self.get_root_xml()

        search_service = NewsApiSearchServiceAsync()
        response = await search_service.process_web_request(request)

        for item in response.body.get("_items"):
            try:
                complete_item = await search_service.service.find_by_id_raw(item.get("_id"))
                if not complete_item:
                    continue

                await remove_unpermissioned_embeds(complete_item, SectionEnum.NEWS_API)
                entry = SubElement(channel, self.item_field)
                self.format_item(entry, complete_item, token)

            except Exception as ex:
                logger.exception("processing {} - {}".format(item.get("_id"), ex))

        return Response(
            XML_ROOT + etree.tostring(feed, method="xml", pretty_print=True).decode("utf-8"),
            headers=[("Content-Type", self.mimetype)],
        )

    def get_root_xml(self) -> tuple[Element, Element]:
        feed = Element("rss", attrib={"version": "2.0"}, nsmap=self.nsmap)
        channel = SubElement(feed, "channel")
        title = self.get_title()
        SubElement(channel, "title").text = title
        SubElement(channel, "description").text = title
        SubElement(channel, "link").text = url_for("rss.get_rss_authed", _external=True)

        return feed, channel

    def get_title(self) -> str:
        site_name = get_app_config("SITE_NAME")
        return f"{site_name} {self.name}"

    def format_item(self, entry: SubElement, item: dict, token: str | None) -> None:
        self.set_item_id(entry, item)
        self.set_item_state(entry, item)
        self.set_item_details(entry, item)
        self.set_item_link(entry, item, token)
        self.set_item_categories(entry, item)
        update_embed_urls(item, token)
        self.set_item_content(entry, item)

        try:
            if item["associations"]["featuremedia"]["renditions"]:
                self.set_item_featuremedia_details(entry, item["associations"]["featuremedia"], token)
        except (KeyError, TypeError):
            pass

    def format_date(self, date_value: str | datetime) -> str:
        date = str_to_date(date_value) if isinstance(date_value, str) else date_value
        iso8601 = date.isoformat()
        if date.tzinfo:
            return iso8601
        return iso8601 + "Z"

    def format_update_date(self, date_value: str | datetime) -> str:
        date = str_to_date(date_value) if isinstance(date_value, str) else date_value
        DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
        return date.strftime(DATETIME_FORMAT) + "Z"

    def set_item_id(self, entry: SubElement, item: dict) -> None:
        # If the item has any parents we use the id of the first, this should be constant throught the update
        # history
        ancestors = item.get("ancestors") or []
        if len(ancestors):
            SubElement(entry, self.item_id_field).text = ancestors[0]
        else:
            SubElement(entry, self.item_id_field).text = item.get("_id")

    def set_item_state(self, entry: SubElement, item: dict) -> None:
        if item.get("pubstatus") == "usable":
            SubElement(
                entry, QName(self.nsmap.get("dcterms"), "valid")
            ).text = "start={}; end={}; scheme=W3C-DTF".format(
                self.format_date(utcnow()), self.format_date(utcnow() + timedelta(days=30))
            )
        else:
            # in effect a kill set the end date into the past
            SubElement(
                entry, QName(self.nsmap.get("dcterms"), "valid")
            ).text = "start={}; end={}; scheme=W3C-DTF".format(
                self.format_date(utcnow()), self.format_date(utcnow() - timedelta(days=30))
            )

    def set_item_details(self, entry: SubElement, item: dict) -> None:
        SubElement(entry, "title").text = CDATA(item.get("headline"))

        firstpublished = str_to_date(item.get("firstpublished"))
        if firstpublished:
            SubElement(entry, "pubDate").text = format_datetime(firstpublished)
        else:
            # ``firstpublished`` should always have a value, nonetheless log this warning and calm type checkers
            logger.warning(f"No firstpublished date for {item.get('_id')}")

        versioncreated = item.get("versioncreated")
        if versioncreated:
            SubElement(entry, QName(self.nsmap.get("dcterms"), "modified")).text = self.format_update_date(
                versioncreated
            )
        else:
            # ``versioncreated`` should always have a value, nonetheless log this warning and calm type checkers
            logger.warning(f"No versioncreated date for {item.get('_id')}")

        byline = item.get("byline")
        if byline:
            # name = item.get("byline")
            if (
                item.get("source")
                and not get_app_config("COPYRIGHT_HOLDER", "").lower() == item.get("source", "").lower()
            ):
                source = item.get("source")
                if source:
                    byline += f" - {source}"
            SubElement(entry, QName(self.nsmap.get("dc"), "creator")).text = byline
        else:
            SubElement(entry, QName(self.nsmap.get("dc"), "creator")).text = (
                item.get("source") if item.get("source") else get_app_config("COPYRIGHT_HOLDER", "")
            )

        SubElement(entry, "source", attrib={"url": url_for("rss.get_rss_authed", _external=True)}).text = item.get(
            "source", ""
        )

        SubElement(entry, "description").text = CDATA(item.get("description_text", ""))

    def set_item_link(self, entry: SubElement, item: dict, token: str | None) -> None:
        url_kwargs = {
            "item_id": item.get("_id"),
            "format": "TextFormatter",
            "_external": True,
        }

        # Conditionally add the 'token' to url_kwargs
        if token:
            url_kwargs["token"] = token

        # Create the SubElement with the dynamically generated href
        SubElement(
            entry,
            "link",
            attrib={
                "rel": "self",
                "href": url_for("news/item.get_item", **url_kwargs),
            },
        )

    def set_item_categories(self, entry: SubElement, item: dict) -> None:
        categories = (
            [{"name": s.get("name")} for s in item.get("service", [])]
            + [{"name": s.get("name")} for s in item.get("subject", [])]
            + [{"name": s.get("name")} for s in item.get("place", [])]
            + [{"name": k} for k in item.get("keywords", [])]
        )
        for category in categories:
            SubElement(entry, "category").text = category.get("name")

    def set_item_content(self, entry: SubElement, item: dict) -> None:
        SubElement(entry, QName(self.nsmap.get("content"), "encoded")).text = CDATA(item.get("body_html", ""))

    def set_item_featuremedia_details(self, entry: SubElement, featuremedia: dict, token: str | None) -> None:
        try:
            image: dict | None = featuremedia["renditions"]["16-9"]
        except (KeyError, TypeError):
            image = None

        if not image:
            # 16x9 rendition not found, not including featuremedia details
            return

        url = (
            url_for("assets.get_item", _external=True, asset_id=image.get("media"), token=token)
            if token
            else url_for("assets.get_item", _external=True, asset_id=image.get("media"))
        )

        media = SubElement(
            entry,
            QName(self.nsmap.get("media"), "content"),
            attrib={
                "url": url,
                "type": image.get("mimetype"),
                "medium": "image",
            },
        )
        SubElement(media, QName(self.nsmap.get("media"), "credit")).text = featuremedia.get("byline")
        SubElement(media, QName(self.nsmap.get("media"), "title")).text = featuremedia.get("description_text")
        SubElement(media, QName(self.nsmap.get("media"), "text")).text = featuremedia.get("body_text")

        poi: dict | None = image.get("poi")
        if poi:
            focr = SubElement(media, QName(self.nsmap.get("mi"), "focalRegion"))
            SubElement(focr, QName(self.nsmap.get("mi"), "x1")).text = str(poi.get("x"))
            SubElement(focr, QName(self.nsmap.get("mi"), "x2")).text = str(poi.get("x"))
            SubElement(focr, QName(self.nsmap.get("mi"), "y1")).text = str(poi.get("y"))
            SubElement(focr, QName(self.nsmap.get("mi"), "y2")).text = str(poi.get("y"))
