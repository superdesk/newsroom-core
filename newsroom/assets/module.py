from newsroom import MONGO_PREFIX
from superdesk.core.module import Module, SuperdeskAsyncApp
from superdesk.core.config import ConfigModel
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


class AssetsConfig(ConfigModel):
    register_upload_endpoint: bool = True


def legacy_init_app(app: SuperdeskAsyncApp):
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

    if assets_config.register_upload_endpoint:
        app.wsgi.register_endpoint(assets_endpoints)


assets_endpoints = EndpointGroup(ASSETS_ENDPOINT_GROUP_NAME, __name__)
assets_config = AssetsConfig()
module = Module(
    name="newsroom.assets",
    init=legacy_init_app,
    resources=[upload_model_config],
    config=assets_config,
    config_prefix="ASSETS",
)
