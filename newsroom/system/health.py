import logging

from superdesk.core import get_app_config
from superdesk.core.types import Response
from superdesk.core.web import EndpointGroup
from superdesk.system.health import get_health_status


logger = logging.getLogger(__name__)
health_endpoints = EndpointGroup("system_health", __name__, auth=False)


@health_endpoints.endpoint("/system/health", methods=["GET"])
async def health():
    """
    Health check endpoint for the system.

    Returns a JSON response containing the application name, the status of various health checks,
    and an overall system status.
    """
    app_name = get_app_config("SITE_NAME", "Newshub")

    return Response(get_health_status(app_name))
