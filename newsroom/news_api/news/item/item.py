from bson import ObjectId

from superdesk.core import get_current_app
from superdesk.core.types import BaseModel, Request, Response
from superdesk.core.module import Module
from superdesk.core.web import EndpointGroup
from superdesk import get_resource_service
from newsroom.news_api.utils import post_api_audit
from newsroom.history_async import HistoryService


news_item_endpoints = EndpointGroup("news/item", __name__)


class RouteArguments(BaseModel):
    item_id: str


class RouteParams(BaseModel):
    format: str = "NINJSFormatter"
    version: str | None = None


@news_item_endpoints.endpoint("news/item/<path:item_id>", methods=["GET"])
async def get_item(args: RouteArguments, params: RouteParams, request: Request) -> Response:
    app = get_current_app()
    service = get_resource_service("formatters")
    formatted = await service.get_version(args.item_id, params.version, params.format)
    mimetype = formatted.get("mimetype")
    response = app.response_class(response=formatted.get("formatted_item"), status=200, mimetype=mimetype)

    await post_api_audit(request, [args.item_id])

    # Record the retrieval of the item in the history collection
    company_id = request.storage.request.get("company_id")
    await HistoryService().create_history_record(
        [{"_id": args.item_id, "version": formatted.get("version")}],
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
