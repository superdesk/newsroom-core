from lxml import etree

from .base import BaseFormatter, NewsroomNITFFormatter


class NITFFormatter(BaseFormatter):

    MIMETYPE = 'application/xml'
    FILE_EXTENSION = 'xml'

    encoding = 'utf-8'
    formatter = NewsroomNITFFormatter()

    def format_item(self, item, item_type='items'):
        dest = {}
        nitf = self.formatter.get_nitf(item, dest, '')
        return etree.tostring(nitf, xml_declaration=True, pretty_print=True, encoding=self.encoding)
