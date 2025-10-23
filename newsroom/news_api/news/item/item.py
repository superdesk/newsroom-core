from datetime import timedelta
from bson import ObjectId

from superdesk.core import get_current_app
from superdesk.core.types import BaseModel, Request, Response
from superdesk.core.module import Module
from superdesk.core.web import EndpointGroup
from superdesk.utc import utcnow

from newsroom.types import WireItem, SectionEnum
from newsroom.wire.embeds import apply_company_permissions_to_embeds, update_embed_urls, set_association_links
from newsroom.formatters import get_formatter_by_classname
from newsroom.settings import get_setting
from newsroom.news_api.utils import post_api_audit
from newsroom.history_async import HistoryService


news_item_endpoints = EndpointGroup("news/item", __name__)


class RouteArguments(BaseModel):
    item_id: str


class RouteParams(BaseModel):
    format: str = "NINJSFormatter"


@news_item_endpoints.endpoint("news/item/<path:item_id>", methods=["GET"])
async def get_item(args: RouteArguments, params: RouteParams, request: Request) -> Response:
    app = get_current_app()
    formatter = get_formatter_by_classname(params.format)
    if not formatter or SectionEnum.NEWS_API not in formatter.sections:
        return await request.abort(400)

    item = await WireItem.get_service().find_by_id(args.item_id)
    time_limit = int(get_setting("news_api_time_limit_days") or 0)
    if not item:
        return await request.abort(404)
    # Ensure that the item has not expired
    elif time_limit > 0 and utcnow() - timedelta(days=time_limit) > item.versioncreated:
        return await request.abort(404)

    item_dict = item.to_dict()
    await apply_company_permissions_to_embeds([item_dict], SectionEnum.NEWS_API)
    await update_embed_urls(item_dict, None)
    set_association_links(item_dict)
    formatted_item = await formatter.format_item(item_dict)

    response = app.response_class(response=formatted_item, status=200, mimetype=formatter.MIMETYPE)

    await post_api_audit(request, [args.item_id])

    # Record the retrieval of the item in the history collection
    company_id = request.storage.request.get("company_id")
    await HistoryService().create_history_record(
        [item_dict],
        "api",
        None,
        ObjectId(company_id) if company_id else None,
        "news_api",
    )
    return response


module = Module(
    "newsroom.news_api.news.item",
    endpoints=[news_item_endpoints],
)
