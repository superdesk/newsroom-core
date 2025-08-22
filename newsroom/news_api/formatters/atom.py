import logging
from datetime import timedelta

from lxml.etree import Element, SubElement, CDATA, QName

from superdesk.core import get_app_config
from superdesk.flask import url_for
from superdesk.utc import utcnow

from .rss import RSSFormatter


logger = logging.getLogger(__name__)


class AtomFormatter(RSSFormatter):
    name: str = "Atom Feed"
    mimetype: str = "application/atom+xml; charset=utf-8"
    nsmap: dict = {
        None: "http://www.w3.org/2005/Atom",
        "dcterms": "http://purl.org/dc/terms/",
        "media": "http://search.yahoo.com/mrss/",
        "mi": "http://schemas.ingestion.microsoft.com/common/",
    }
    item_field: str = "entry"
    item_id_field: str = "id"

    def get_root_xml(self) -> tuple[Element, Element]:
        feed = Element("feed", nsmap=self.nsmap)
        SubElement(feed, "title").text = CDATA(self.get_title())
        SubElement(feed, "updated").text = self.format_update_date(utcnow())
        SubElement(SubElement(feed, "author"), "name").text = get_app_config("SITE_NAME")
        SubElement(feed, "id").text = url_for("atom.get_atom_authed", _external=True)
        SubElement(
            feed,
            "link",
            attrib={"href": url_for("atom.get_atom_authed", _external=True), "rel": "self"},
        )
        return feed, feed

    def set_item_state(self, entry: SubElement, item: dict) -> None:
        if item.get("pubstatus") == "usable":
            SubElement(
                entry, QName(self.nsmap.get("dcterms"), "valid")
            ).text = "start={}; end={}; scheme=W3C-DTF".format(
                self.format_date(utcnow()),
                self.format_date(utcnow() + timedelta(days=30)),
            )
        else:
            # in effect a kill set the end date into the past
            SubElement(
                entry, QName(self.nsmap.get("dcterms"), "valid")
            ).text = "start={}; end={}; scheme=W3C-DTF".format(
                self.format_date(utcnow()),
                self.format_date(utcnow() - timedelta(days=30)),
            )

    def set_item_details(self, entry: SubElement, item: dict) -> None:
        SubElement(entry, "title").text = CDATA(item.get("headline"))

        firstpublished = item.get("firstpublished")
        if firstpublished:
            SubElement(entry, "published").text = self.format_date(firstpublished)
        else:
            # ``firstpublished`` should always have a value, nonetheless log this warning and calm type checkers
            logger.warning(f"No firstpublished date for {item.get('_id')}")

        versioncreated = item.get("versioncreated")
        if versioncreated:
            SubElement(entry, "updated").text = self.format_update_date(versioncreated)
        else:
            # ``versioncreated`` should always have a value, nonetheless log this warning and calm type checkers
            logger.warning(f"No versioncreated date for {item.get('_id')}")

        if item.get("byline"):
            SubElement(SubElement(entry, "author"), "name").text = item.get("byline")

        SubElement(entry, "summary").text = CDATA(item.get("description_text", ""))

    def set_item_categories(self, entry: SubElement, item: dict) -> None:
        categories = [{"name": s.get("name")} for s in item.get("service", [])]
        for category in categories:
            SubElement(entry, "category", attrib={"term": category.get("name")})

    def set_item_content(self, entry: SubElement, item: dict) -> None:
        SubElement(entry, "content", attrib={"type": "html"}).text = CDATA(item.get("body_html", ""))
