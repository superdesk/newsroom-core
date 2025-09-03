import json

from quart_babel import gettext

from superdesk.core import get_app_config
from content_api.errors import BadParameterValueError


from newsroom.search.utils import query_string
from newsroom.products.service import ProductsService
from newsroom.search.types import NewshubSearchRequest
from newsroom.products.utils import get_products_by_company_async
from newsroom.auth.utils import get_company_or_none_from_request

from .filters_utils import create_date_range_filter, get_date_range
from .types import NewsApiSearchRequestArgs, default_allowed_exclude_fields


async def prefill_company(request: NewshubSearchRequest[NewsApiSearchRequestArgs]) -> None:
    """
    Gets company from web_request and prefills it into request.
    If not company is found, it raises an exception.
    """
    if request.company is not None:
        return
    request.company = get_company_or_none_from_request(request.web_request)

    if request.company is None:
        raise BadParameterValueError(gettext("Invalid search request, company not found"))


async def prefill_products(request: NewshubSearchRequest[NewsApiSearchRequestArgs]):
    """Prefill the search products"""

    products_service = ProductsService()
    assert request.company is not None

    if request.args.product_ids:
        cursor = await products_service.find(
            {"is_enabled": True, "companies": request.company.id, "_id": {"$in": request.args.product_ids}},
        )
        request.products = await cursor.to_list()
        valid_product_ids = set(item.id for item in request.products)
        if not all(product in valid_product_ids for product in request.args.product_ids):
            raise BadParameterValueError(gettext("Bad product value"))
    else:
        request.products = await get_products_by_company_async(request.company, product_type=request.section)


def validate_page(request: NewshubSearchRequest[NewsApiSearchRequestArgs]):
    """Validate the page params"""
    query_max_page_size = get_app_config("QUERY_MAX_PAGE_SIZE")

    if request.args.page_size > query_max_page_size:
        raise BadParameterValueError(
            "Requested maximum number of results exceeds {max}".format(max=query_max_page_size)
        )
    elif (request.args.page - 1) * request.args.page_size >= 1000:
        # https://www.elastic.co/guide/en/elasticsearch/guide/current/pagination.html#pagination
        raise BadParameterValueError("Page limit exceeded")


def apply_filter_fields(request: NewshubSearchRequest[NewsApiSearchRequestArgs]):
    """Generate the field filters"""

    # filter fields and elasticsearch keys
    argument_fields = {
        "service": "service.code",
        "subject": "subject.code",
        "urgency": "urgency",
        "priority": "priority",
        "genre": "genre.code",
        "item_source": "source",
    }

    filters = []
    for argument_name, field_name in argument_fields.items():
        filter_value = getattr(request.args, argument_name)

        if filter_value is None:
            continue

        try:
            filter_value = json.loads(filter_value)
        except Exception:
            pass

        if not filter_value:
            raise BadParameterValueError(f"Bad parameter value for Parameter ({argument_name})")

        if not isinstance(filter_value, list):
            filter_value = [filter_value]

        filters.append({"terms": {field_name: filter_value}})

    if filters:
        request.search.query.filter.extend(filters)


def apply_date_filter(request: NewshubSearchRequest[NewsApiSearchRequestArgs]):
    """Generate and apply date filters"""

    start_date, end_date = get_date_range(request.args)
    date_filter = create_date_range_filter(start_date, end_date)

    if date_filter:
        request.search.query.filter.append(date_filter)


def apply_request_filter(request: NewshubSearchRequest[NewsApiSearchRequestArgs]):
    """Generate the filters from request args"""

    if request.args.q:
        request.search.query.filter.append(query_string(request.args.q, request.args.default_operator))


def apply_projection(request: NewshubSearchRequest[NewsApiSearchRequestArgs]):
    """Create a projection object that explicitly includes particular content fields from results."""

    default_fields = {
        "_id",
        "uri",
        "embargoed",
        "pubstatus",
        "ednote",
        "signal",
        "copyrightnotice",
        "copyrightholder",
        "versioncreated",
        "evolvedfrom",
        "original_id",
        "body_html",
    }

    include_fields = default_fields.union(default_allowed_exclude_fields)

    # provided in request, then let's join them with default_fields instead
    if request.args.include_fields:
        include_fields = default_fields.union(request.args.include_fields)

    # given include and exclude are mutually exclusive in the ESQuery and in request
    # we need to remove the exclude_fields from include_fields here
    for field in request.args.exclude_fields or []:
        include_fields.remove(field)

    request.search.include_fields = include_fields
