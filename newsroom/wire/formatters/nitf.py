from typing import Any
from lxml import etree
from quart_babel import lazy_gettext

from superdesk.publish.formatters.nitf_formatter import NITFFormatter as SuperdeskNITFFormatter
from superdesk.etree import parse_html

from newsroom.types import SectionEnum
from newsroom.formatters import BaseFormatter, FormatterAssetType


class NewsroomNITFFormatter(SuperdeskNITFFormatter):
    def map_html_to_xml(self, element, html):
        """
        Map the html text tags to xml

        :param etree.Element element: The xml element to populate
        :param str html: the html to parse the text from
        :return:
        """

        root = parse_html(html, content="html")
        # if there are no ptags just br
        if not len(root.xpath("//p")) and len(root.xpath("//br")):
            para = etree.SubElement(element, "p")
            for br in root.xpath("//br"):
                etree.SubElement(para, "br").text = br.text

        for p in root.xpath("//p|figure"):
            if p.tag == "figure":
                captions = p.xpath(".//figcaption")
                if len(captions):
                    para = etree.SubElement(element, "p")
                    para.text = etree.tostring(captions[0], encoding="unicode", method="text")
            else:
                para = etree.SubElement(element, "p")
                if len(p.xpath(".//br")) > 0:
                    for br in p.xpath(".//br"):
                        etree.SubElement(para, "br").text = br.text
                para.text = etree.tostring(p, encoding="unicode", method="text")

        # there neither ptags pr br's
        if len(list(element)) == 0:
            etree.SubElement(element, "p").text = etree.tostring(root, encoding="unicode", method="text")


class NITFFormatter(BaseFormatter):
    format_id = "nitf"
    name = lazy_gettext("NITF")
    sections = [SectionEnum.WIRE, SectionEnum.NEWS_API]
    assets = [FormatterAssetType.TEXT]

    MIMETYPE = "application/xml"
    FILE_EXTENSION = "xml"

    encoding = "utf-8"
    formatter = NewsroomNITFFormatter()

    def _format_docdata_doc_id_source(self, article, docdata):
        elem = docdata.find(".//head/docdata/doc-id")
        if elem is not None:
            elem.set("regsrc", article.get("source", ""))

    async def format_item(self, item: dict[str, Any], item_type: str | None = "items") -> bytes:
        dest: dict[str, Any] = {}
        nitf = self.formatter.get_nitf(item, dest, "")
        self._format_docdata_doc_id_source(item, nitf)
        return etree.tostring(nitf, xml_declaration=True, pretty_print=True, encoding=self.encoding)
