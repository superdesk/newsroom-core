from typing import Any
from io import BytesIO
from datetime import date
from collections import OrderedDict

from xhtml2pdf import pisa
from werkzeug.utils import secure_filename

from superdesk.core import get_app_config
from superdesk.flask import render_template
from superdesk.utc import utcnow, utc_to_local

from newsroom.types import MonitoringProfileResourceModel
from newsroom.wire.formatters.base import BaseFormatter


class MonitoringPDFFormatter(BaseFormatter):
    FILE_EXTENSION = "pdf"
    MIMETYPE = "application/pdf"

    def format_filename(self, item: dict[str, Any]) -> str:
        attachment_filename = "%s-monitoring-export.pdf" % utcnow().strftime("%Y%m%d%H%M%S")
        return secure_filename(attachment_filename)

    async def get_monitoring_file(
        self,
        date_items_dict: OrderedDict[date, list[dict[str, Any]]],
        monitoring_profile: MonitoringProfileResourceModel,
    ) -> BytesIO:
        if not date_items_dict:
            return BytesIO()

        data = {
            "date_items_dict": date_items_dict,
            "monitoring_profile": monitoring_profile,
            "current_date": utc_to_local(get_app_config("DEFAULT_TIMEZONE"), utcnow()).strftime("%d/%m/%Y"),
            "monitoring_report_name": get_app_config("MONITORING_REPORT_NAME", "Newsroom"),
        }
        exported_html = str.encode(await render_template("monitoring_export.html", **data), "utf-8")
        pdf_context = pisa.CreatePDF(exported_html)
        pdf_file = pdf_context.dest
        pdf_file.seek(0)
        return pdf_file
