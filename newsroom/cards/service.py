from typing import List, Any

from newsroom.core.resources import NewshubAsyncResourceService
from newsroom.flask import get_file_from_request
from newsroom.assets import save_file_and_get_url


from newsroom.types import CardResourceModel, DashboardCardConfig, DashboardCardType


class CardsResourceService(NewshubAsyncResourceService[CardResourceModel]):
    async def on_create(self, docs: list[CardResourceModel]) -> None:
        await super().on_create(docs)
        for doc in docs:
            await self._update_config(doc.dashboard_type, doc.config or {})

    async def on_created(self, docs: List[CardResourceModel]) -> None:
        await super().on_created(docs)
        self._delete_caches()

    async def on_update(self, updates: dict[str, Any], original: CardResourceModel) -> None:
        await super().on_update(updates, original)

        if updates.get("config"):
            await self._update_config(updates.get("type") or original.dashboard_type, updates["config"])

    async def on_updated(self, updates: dict[str, Any], original: CardResourceModel) -> None:
        await super().on_updated(updates, original)
        self._delete_caches()

    async def on_deleted(self, doc: CardResourceModel) -> None:
        await super().on_deleted(doc)
        self._delete_caches()

    def _delete_caches(self):
        from newsroom.wire.views import delete_dashboard_caches

        delete_dashboard_caches()

    async def _update_config(self, dashboard_type: DashboardCardType, config: DashboardCardConfig) -> None:
        if dashboard_type == DashboardCardType.EVENTS_2x2 and config.get("events"):
            for index, event in enumerate(config["events"]):
                file = await get_file_from_request(f"file{index}")

                if file:
                    file_url = await save_file_and_get_url(file)
                    if file_url:
                        event["file_url"] = file_url
        elif dashboard_type == DashboardCardType.PHOTO_GALLERY_4 and config.get("sources"):
            for source in config["sources"]:
                if source.get("url") and source.get("count"):
                    try:
                        source["count"] = int(source["count"])
                    except ValueError:
                        source.pop("url", None)
                        source.pop("count", None)
                else:
                    source.pop("url", None)
                    source.pop("count", None)
