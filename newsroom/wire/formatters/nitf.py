from lxml import etree

from .base import BaseFormatter, NewsroomNITFFormatter


class NITFFormatter(BaseFormatter):

    MIMETYPE = 'application/xml'
    FILE_EXTENSION = 'xml'

    encoding = 'utf-8'
    formatter = NewsroomNITFFormatter()

    def _format_docdata_doc_id_source(self, article, docdata):
        elem = docdata.find('.//head/docdata/doc-id')
        if elem is not None:
            elem.set('regsrc', article.get('source', ''))

    def format_item(self, item, item_type='items'):
        dest = {}
        nitf = self.formatter.get_nitf(item, dest, '')
        self._format_docdata_doc_id_source(item, nitf)
        return etree.tostring(nitf, xml_declaration=True, pretty_print=True, encoding=self.encoding)
