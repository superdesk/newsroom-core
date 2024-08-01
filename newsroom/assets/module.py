from superdesk.core.module import Module
from superdesk.core.web import Response, EndpointGroup, Request
from superdesk.core.resources import ResourceModel, ResourceConfig


ASSETS_RESOURCE = "upload"


class Upload(ResourceModel):
    """Necessary Resource so `GridFSMediaStorageAsync` would work"""

    pass


upload_model_config = ResourceConfig(
    name="upload",
    data_class=Upload,
    elastic=None,
)


assets_endpoints = EndpointGroup(ASSETS_RESOURCE, __name__)
module = Module(name="newsroom.assets", resources=[upload_model_config], endpoints=[assets_endpoints])
