from superdesk.core.module import Module
from superdesk.core.web import EndpointGroup
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


def legacy_init_app(app):
    # TODO: remove this once we fully moved into async storage
    # Keeping this only for compatibility with `sync` media storage
    from .utils import upload_url

    app.wsgi.upload_url = upload_url


assets_endpoints = EndpointGroup(ASSETS_RESOURCE, __name__)
module = Module(
    name="newsroom.assets", init=legacy_init_app, resources=[upload_model_config], endpoints=[assets_endpoints]
)
