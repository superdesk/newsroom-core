from superdesk.flask import abort
from pydantic import BaseModel
import logging

from superdesk.core import get_app_config, get_current_async_app
from superdesk.core.types import Response, Request
from superdesk.flask import request as flask_request
from superdesk.storage.superdesk_file import get_file_request_range, generate_response_for_file

from .module import assets_endpoints
from .utils import get_media_file, get_content_disposition
from newsroom.history_async import HistoryService
from newsroom.types import WireItem, SectionEnum
from newsroom.auth.utils import get_user_or_none_from_request
from newsroom.products.utils import get_products_for_request_user_and_company

logger = logging.getLogger(__name__)


class RouteArguments(BaseModel):
    media_id: str


class UrlParams(BaseModel):
    filename: str | None = None


class DownloadUrlParams(BaseModel):
    filename: str | None = None
    item_id: str | None = None


async def get_upload(media_id: str, filename: str | None = None):
    begin, end = get_file_request_range(flask_request.range if flask_request else None)
    media_file = await get_media_file(media_id, begin=begin, end=end)
    if not media_file:
        return None

    return await generate_response_for_file(
        media_file, content_disposition=get_content_disposition(filename, media_file.content_type)
    )


@assets_endpoints.endpoint("/assets/<path:media_id>", methods=["GET"], auth=False)
async def download_file(args: RouteArguments, params: UrlParams, request: Request) -> Response:
    # Allow access to ``/assets/<media_id>`` if PUBLIC_DASHBOARD is enabled or is a valid session
    if not get_app_config("PUBLIC_DASHBOARD"):
        response = await get_current_async_app().auth.authenticate(request)
        if response:
            return response

    response = await get_upload(args.media_id, params.filename)
    return response if response else await request.abort(404)


@assets_endpoints.endpoint("/assets/<path:media_id>/download", methods=["GET", "HEAD"])
async def download_file_logged(args: RouteArguments, params: DownloadUrlParams, request: Request) -> Response:
    """
    Download and log the download. Accepts a HEAD request that will validate that the user has the rights to download
    the asset.
    @param args: Contains the media_id, the unique identifier for the asset.
    @param params: item_id The of the parent item.
                   and the suggested filename for the attachment.
    @param request: The incoming HTTP request object.
    @return: A Response object containing the file stream (GET) or a success
             status (HEAD) if the item is allowed to be downloaded , otherwise aborts with 403 or 404.
    """
    if params.item_id:
        item: WireItem = await WireItem.get_service().find_by_id(params.item_id)
        if not item:
            logger.warning(f"Failed to find item for media download for {params.item_id} with media id {args.media_id}")
            abort(404)

        name, association = _find_association(item, args.media_id)

        sdesk_products: set[str] = {
            product.sd_product_id
            for product in await get_products_for_request_user_and_company(SectionEnum.WIRE)
            if product.sd_product_id and product.is_enabled
        }

        products = association.get("products", [])
        if not isinstance(products, list):
            products = []
        association_products = {a.get("code") for a in products if isinstance(a, dict) and a.get("code")}

        if not (sdesk_products & association_products):
            abort(403)

        if request.method == "GET":
            user = get_user_or_none_from_request(request)
            action = f"download {association.get('type')}"
            if user:
                await HistoryService().create_media_history_record(item.to_dict(), name, action, user)
            else:
                abort(404)
    else:
        abort(404)

    if request.method == "HEAD":
        return Response("", 204)

    response = await get_upload(args.media_id, params.filename)
    if not response:
        abort(404)

    return response


def _find_association(item, media_id):
    """
    Find the matching media association in the item
    :param item: item object
    :param media_id: ID of the media
    :return: tuple (name, association) or a 404
    """
    for name, association in (item.associations or {}).items():
        renditions = association.get("renditions", {})
        for rend_key, rend_data in renditions.items():
            if rend_data.get("media") == media_id:
                return name, association
    abort(404)
