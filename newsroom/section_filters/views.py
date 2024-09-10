import re
import json
from typing import Any, Dict, Optional

from bson import ObjectId
from quart import abort
from quart_babel import gettext
from pydantic import BaseModel, ValidationError, field_validator

from superdesk.core.web import EndpointGroup, Response, Request

from newsroom.decorator import admin_only
from newsroom.core import get_current_wsgi_app
from newsroom.utils import create_or_abort, get_json_or_400, response_from_validation

from .service import SectionFiltersService
from .model import SectionFilter

section_filters_endpoints = EndpointGroup("section_filters", __name__)


async def get_settings_data():
    """Get the settings data for section filter

    :param context
    """
    all_filters = [obj async for obj in SectionFiltersService().get_all_raw()]

    data = {
        "section_filters": all_filters,
        "sections": get_current_wsgi_app().sections,
    }

    return data


def validate_section_filter(section_filter: dict) -> Response | None:
    if not section_filter.get("name"):
        return Response({"name": gettext("Name not found")}, 400, ())
    return None


async def get_section_filter_or_abort(id: str) -> SectionFilter:
    section_filter = await SectionFiltersService().find_by_id(id)
    if section_filter is None:
        abort(404)

    return section_filter


class IndexParams(BaseModel):
    q: Optional[Dict[str, Any]] = None

    @field_validator("q", mode="before")
    def parse_where(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        return value


@section_filters_endpoints.endpoint("/section_filters", methods=["GET"])
@admin_only
async def index(_a: None, params: IndexParams, _r: None):
    cursor = await SectionFiltersService().search(lookup=params.q)
    section_filters = await cursor.to_list_raw()
    return Response(section_filters)


class SearchParams(BaseModel):
    q: str | None = None


@section_filters_endpoints.endpoint("/section_filters/search", methods=["GET"])
@admin_only
async def search(_a: None, params: SearchParams, _q: Request):
    lookup = None
    if params.q:
        regex = re.compile(".*{}.*".format(params.q), re.IGNORECASE)
        lookup = {"name": regex}

    cursor = await SectionFiltersService().search(lookup=lookup)
    section_filters = await cursor.to_list_raw()
    return Response(section_filters)


@section_filters_endpoints.endpoint("/section_filters/new", methods=["POST"])
@admin_only
async def create():
    creation_data = await get_json_or_400()
    app_sections = get_current_wsgi_app().sections

    section = next(
        (s for s in app_sections if s["_id"] == creation_data.get("filter_type")),
        None,
    )
    if section and section.get("search_type"):
        creation_data["search_type"] = section["search_type"]
    creation_data["id"] = ObjectId()

    section_filter_id = await create_or_abort(SectionFiltersService, SectionFilter, creation_data)

    return Response({"success": True, "_id": section_filter_id}, 201)


class DetailArgs(BaseModel):
    id: str


@section_filters_endpoints.endpoint("/section_filters/<string:id>", methods=["POST"])
@admin_only
async def edit(args: DetailArgs, _p: None, _q: None):
    await get_section_filter_or_abort(args.id)

    data = await get_json_or_400()
    updates = {
        "name": data.get("name"),
        "description": data.get("description"),
        "sd_product_id": data.get("sd_product_id"),
        "query": data.get("query"),
        "is_enabled": data.get("is_enabled"),
        "filter_type": data.get("filter_type", "wire"),
    }

    try:
        await SectionFiltersService().update(args.id, updates)
        return Response({"success": True})
    except ValidationError as err:
        return response_from_validation(err)


@section_filters_endpoints.endpoint("/section_filters/<string:id>", methods=["DELETE"])
@admin_only
async def delete(args: DetailArgs, _p: None, _r: None):
    """Deletes the section_filters by given id"""

    section_filter = await get_section_filter_or_abort(args.id)
    await SectionFiltersService().delete(section_filter)

    return Response({"success": True})
