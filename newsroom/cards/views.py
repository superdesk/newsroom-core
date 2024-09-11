import re

from pydantic import BaseModel

from superdesk.core import json
from superdesk.core.web import Request, Response, EndpointGroup
from superdesk.core.resources.fields import ObjectId as ObjectIdField

from newsroom.decorator import admin_only, login_required

from .service import CardsResourceService


cards_endpoints = EndpointGroup("cards", __name__)


@cards_endpoints.endpoint("/cards", methods=["GET"])
@login_required
async def index() -> Response:
    return Response(await (await CardsResourceService().find({})).to_list_raw(), 200, ())


class CardSearchParams(BaseModel):
    q: str | None = None
    sort: str | None = None
    max_results: int = 250
    page: int = 1


@cards_endpoints.endpoint("/cards/search", methods=["GET"])
@admin_only
async def search(args: None, params: CardSearchParams, request: Request) -> Response:
    return Response(
        await (
            await CardsResourceService().find(
                {} if not params.q else {"label": re.compile(".*{}.*".format(params.q), re.IGNORECASE)},
                sort=params.sort,
                max_results=params.max_results,
                page=params.page,
            )
        ).to_list_raw(),
        200,
        (),
    )


@cards_endpoints.endpoint("/cards/new", methods=["POST"])
@admin_only
async def create(request: Request) -> Response:
    card_data = json.loads((await request.get_form()).get("card"))
    if not card_data:
        request.abort(400)

    service = CardsResourceService()
    if not card_data.get("_id"):
        card_data["_id"] = service.generate_id()

    new_ids = await service.create([card_data])

    return Response({"success": True, "_id": new_ids[0]}, 201, ())


class CardItemUrlArgs(BaseModel):
    id: ObjectIdField


@cards_endpoints.endpoint("/cards/<id>", methods=["POST"])
@admin_only
async def edit(args: CardItemUrlArgs, params: None, request: Request) -> Response:
    service = CardsResourceService()

    card_data = json.loads((await request.get_form()).get("card"))
    if not card_data:
        request.abort(400)

    await service.update(args.id, card_data, etag=request.get_header("If-Match"))

    return Response({"success": True})


@cards_endpoints.endpoint("/cards/<id>", methods=["DELETE"])
@admin_only
async def delete(args: CardItemUrlArgs, params: None, request: Request) -> Response:
    """Deletes the cards by given id"""
    service = CardsResourceService()

    original = await service.find_by_id(args.id)
    if not original:
        request.abort(404)

    await service.delete(original, etag=request.get_header("If-Match"))

    return Response({"success": True})
