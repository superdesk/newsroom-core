from datetime import datetime

from newsroom.agenda.model import FeaturedResourceModel

from superdesk.core.resources import AsyncResourceService
from superdesk.utc import local_to_utc


class FeaturedService(AsyncResourceService[FeaturedResourceModel]):
    resource_name = "agenda_featured"

    async def on_create(self, docs):
        """
        Add UTC from/to datetimes on save.
        Problem is 31.8. in Sydney is from 30.8. 14:00 UTC to 31.8. 13:59 UTC.
        And because we query later using UTC, we store those UTC datetimes as
        display_from and display_to.
        """
        for item in docs:
            date = datetime.strptime(item._id, "%Y%m%d")
            item.display_from = local_to_utc(item.tz, date.replace(hour=0, minute=0, second=0))
            item.display_to = local_to_utc(item.tz, date.replace(hour=23, minute=59, second=59))
        await super().on_create(docs)

    async def find_one_for_date(self, for_date: datetime) -> FeaturedResourceModel | None:
        return await self.find_one(req=None, display_from={"$lte": for_date}, display_to={"$gte": for_date})
