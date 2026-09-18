from typing import Any
from datetime import date
from collections import OrderedDict
from io import BytesIO

from newsroom.types import MonitoringProfileResourceModel, SectionEnum
from newsroom.wire.formatters.text import TextFormatter


class BaseMonitoringFormatter(TextFormatter):
    sections = [SectionEnum.MONITORING]

    async def get_monitoring_file(
        self,
        date_items_dict: OrderedDict[date, list[dict[str, Any]]],
        monitoring_profile: MonitoringProfileResourceModel,
    ) -> BytesIO:
        raise NotImplementedError()
