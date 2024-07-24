from typing import Optional, Dict, Any
from superdesk.core.module import Module
from content_api import MONGO_PREFIX
from superdesk.core.resources import ResourceConfig, AsyncResourceService, MongoResourceConfig, ResourceModel


class UiConfig(ResourceModel):
    preview: Optional[Dict[str, Any]] = None
    details: Optional[Dict[str, Any]] = None
    list: Optional[Dict[str, Any]] = None
    advanced_search_tabs: Optional[Dict[str, Any]] = None
    multi_select_topics: bool = False
    search: Optional[bool] = None
    enable_global_topics: bool = True
    open_coverage_content_in_same_page: bool = False
    subnav: Optional[Dict[str, Any]] = None
    init_version: Optional[int] = None


class UiConfigResourceService(AsyncResourceService[UiConfig]):
    async def get_section_config(self, section_name: str) -> Dict[str, Any]:
        """Get the section config"""
        config = await self.find_by_id(section_name)

        if not config:
            return {}
        return config.dict(by_alias=True, exclude_unset=True)

    async def get_all_config(self) -> dict:
        # Collect all config items asynchronously
        configs = [config async for config in self.get_all()]

        # Use dictionary comprehension to build the result
        return {item.id: item.dict(by_alias=True, exclude_unset=True) for item in configs} if configs else {}


ui_config_model_config = ResourceConfig(
    name="ui_config",
    data_class=UiConfig,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    elastic=None,
    service=UiConfigResourceService,
)

module = Module(name="newsroom.ui_config_async", resources=[ui_config_model_config])
