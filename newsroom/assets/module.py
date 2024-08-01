from newsroom import MONGO_PREFIX
from superdesk.core.module import Module
from superdesk.core.web import EndpointGroup
from superdesk.core.resources import ResourceModel, ResourceConfig


ASSETS_RESOURCE = "upload"
ASSETS_ENDPOINT_GROUP_NAME = "assets"


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
    app.wsgi.config["DOMAIN"].setdefault(
        "upload",
        {
            "authentication": None,
            "mongo_prefix": MONGO_PREFIX,
            "internal_resource": True,
        },
    )


assets_endpoints = EndpointGroup(ASSETS_ENDPOINT_GROUP_NAME, __name__)
module = Module(
    name="newsroom.assets", init=legacy_init_app, resources=[upload_model_config], endpoints=[assets_endpoints]
)
