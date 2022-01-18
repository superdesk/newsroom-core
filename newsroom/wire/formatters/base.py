from lxml import etree

from superdesk.utc import utcnow
from superdesk.publish.formatters.nitf_formatter import NITFFormatter as SuperdeskNITFFormatter
from superdesk.etree import parse_html

from . import FormatterRegistry


class BaseFormatter(metaclass=FormatterRegistry):

    MIMETYPE = None
    FILE_EXTENSION = None
    MEDIATYPE = 'text'

    def format_filename(self, item):
        assert self.FILE_EXTENSION
        _id = (item.get('slugline', item['_id']) or item['_id']).replace(' ', '-').lower()
        timestamp = item.get('versioncreated', item.get('_updated', utcnow()))
        return '{timestamp}-{_id}.{ext}'.format(
            timestamp=timestamp.strftime('%Y%m%d%H%M'),
            _id=_id.lower(),
            ext=self.FILE_EXTENSION)

    def get_mimetype(self, item):
        return self.MIMETYPE

    def get_mediatype(self):
        return self.MEDIATYPE


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
            if p.tag == 'figure':
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
