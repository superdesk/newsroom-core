from typing import cast

from superdesk.core import get_current_app
from superdesk.core.config import ConfigModel


def get_current_wsgi_app():
    from newsroom.web.factory import NewsroomWebApp

    return cast(NewsroomWebApp, get_current_app())


class NewshubModuleConfig(ConfigModel):
    register_endpoints: bool = True
    register_settings: bool = True
