import hmac
import logging
from typing import Any

from superdesk.core import get_app_config
from superdesk.core.web import Request

from newsroom.core import get_current_wsgi_app

logger = logging.getLogger(__name__)

KEY = "PUSH_KEY"


def fix_hrefs(doc: dict[str, Any]):
    if doc.get("renditions"):
        app = get_current_wsgi_app()
        for key, rendition in doc["renditions"].items():
            if rendition.get("media"):
                rendition["href"] = app.upload_url(rendition["media"])
    for assoc in doc.get("associations", {}).values():
        fix_hrefs(assoc)


async def test_signature(request: Request):
    """Test if request is signed using app PUSH_KEY."""
    key = get_app_config(KEY)
    if not key:
        if not get_app_config("TESTING"):
            logger.warning("PUSH_KEY is not configured, can not verify incoming data.")
        return True
    payload = await request.get_data()
    mac = hmac.new(key, payload, "sha1")
    return hmac.compare_digest(request.get_header("x-superdesk-signature"), "sha1=%s" % mac.hexdigest())


async def assert_test_signature(request: Request):
    if not await test_signature(request):
        flask_req = request.request
        logger.warning("signature invalid on push from %s", flask_req.referrer or flask_req.remote_addr)
        await request.abort(403)
