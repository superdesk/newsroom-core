from typing import Any, Callable
from inspect import isawaitable

from quart_babel import gettext

from superdesk.core import get_app_config
from superdesk.core.types import ESQuery
from content_api.errors import BadParameterValueError

from newsroom.types import SectionEnum
from newsroom.exceptions import AuthorizationError
from newsroom.utils import get_local_date, get_end_date
from newsroom.auth.utils import get_user_or_none_from_request, get_company_or_none_from_request, get_user_sections
from newsroom.settings import get_setting

from newsroom.users import UsersService
from newsroom.products import (
    ProductsService,
    get_products_by_company_async,
    get_products_by_user_async,
    get_products_by_navigation_async,
)

from .types import (
    NewshubSearchRequest,
    ElasticDefaultOperator,
    ElasticQueryStringType,
    SearchArgsType,
    SearchFilterFunction,
)
from .utils import query_string, query_string_for_section, get_filter_query
from .config import get_nested_config, get_advanced_search_fields


async def prefill_user(request: NewshubSearchRequest) -> None:
    """Prefill the user from the current request details"""

    request.current_user = get_user_or_none_from_request(request.web_request)
    request.is_admin = request.current_user.is_admin() if request.current_user else False

    if request.user is not None:
        request.is_admin = request.user.is_admin()
        if not request.current_user:
            request.current_user = request.user
        return

    request.is_admin = request.current_user.is_admin() if request.current_user else False
    if request.is_admin and request.args.user_id:
        request.user = await UsersService().find_by_id(request.args.user_id)
        if request.user is None:
            raise BadParameterValueError(gettext("Invalid search request, user not found"))
    else:
        request.user = request.current_user


async def prefill_company(request: NewshubSearchRequest) -> None:
    """Prefill the company from the current user and request details"""

    if request.company is not None:
        return
    elif request.current_user and request.current_user.id == request.args.user_id:
        request.company = get_company_or_none_from_request(request.web_request)
    elif request.user is not None and request.user.company:
        request.company = await request.user.get_company()
        if request.company is None:
            raise BadParameterValueError(gettext("Invalid search request, company not found"))

    if not request.is_admin and request.company is None:
        raise BadParameterValueError(gettext("Invalid search request, company not found"))


async def prefill_products(request: NewshubSearchRequest) -> None:
    """Prefill the available products based on the current user, company and section"""

    if request.section is None:
        # This should not happen, as it's prefilled by search service
        return

    products_service = ProductsService()
    request.products = []
    if request.is_admin:
        if len(request.args.navigation_ids):
            request.products = await get_products_by_navigation_async(
                request.args.navigation_ids, product_type=request.section
            )
        elif len(request.args.product_ids):
            request.products = await products_service.find_by_ids(request.args.product_ids)
    elif request.company is not None:
        if request.args.product_ids:
            allowed_product_ids = (
                [
                    product._id
                    for product in request.company.products
                    if product._id in request.args.product_ids and product.section == request.section.value
                ]
                if request.company is not None and request.company.products is not None
                else []
            )
            request.products = await products_service.find_by_ids(allowed_product_ids)
        else:
            if request.user and request.user.products:
                request.products = await get_products_by_user_async(
                    request.user,
                    request.section,
                    request.args.navigation_ids,
                )

            # add unlimited (seats=0) company products
            company_products = await get_products_by_company_async(
                request.company,
                request.args.navigation_ids,
                product_type=request.section,
                unlimited_only=True,
            )
            if company_products:
                request.products.extend([product for product in company_products if product not in request.products])


def apply_date_range(request: NewshubSearchRequest) -> None:
    """Applies date range filter based on request args"""

    if not request.args.start_date and not request.args.end_date:
        return

    range_query = {}
    offset = int(request.args.timezone_offset or 0)
    if request.args.start_date:
        range_query["gte"] = get_local_date(request.args.start_date, request.args.start_time, offset)
    if request.args.end_date:
        range_query["lte"] = get_end_date(
            request.args.end_date,
            get_local_date(request.args.end_date, request.args.end_time, offset),
        )

    if get_app_config("FILTER_BY_POST_FILTER", False):
        request.search.post_filter.must.append({"range": {"versioncreated": range_query}})
    else:
        request.search.query.must.append({"range": {"versioncreated": range_query}})


def apply_query_string(request: NewshubSearchRequest) -> None:
    """Applies query_string filter based on request args"""

    search_text = request.args.q.strip() if request.args.q else None
    if not search_text:
        return

    fields_config_key = "AGENDA_SEARCH_FIELDS" if request.section == SectionEnum.AGENDA else "WIRE_SEARCH_FIELDS"
    fields = get_app_config(fields_config_key, ["*"])
    request.search.query.must.append(
        query_string(
            search_text,
            default_operator=request.args.default_operator,
            fields=fields,
        )
    )


def apply_ids_filter(request: NewshubSearchRequest) -> None:
    """Applies item IDs filter based on request args"""

    if not len(request.args.ids):
        return

    request.search.query.filter.append({"ids": {"values": request.args.ids}})


def get_apply_filters(get_aggregation_field: Callable[[str], str]) -> SearchFilterFunction:
    """Applies metadata filter(s) based on request args"""

    def apply_filters(request: NewshubSearchRequest) -> None:
        if not request.args.filter:
            return

        if get_app_config("FILTER_AGGREGATIONS", True):
            filters: list[dict[str, Any]] = []
            for key, val in request.args.filter.items():
                if not val:
                    continue
                filters.append(
                    get_filter_query(
                        key,
                        val,
                        get_aggregation_field(key),
                        get_nested_config(
                            "agenda" if request.section == SectionEnum.AGENDA else "items",
                            key,
                        ),
                    )
                )
            if len(filters):
                if get_app_config("FILTER_BY_POST_FILTER", False):
                    request.search.post_filter.must.extend(filters)
                else:
                    request.search.query.must.extend(filters)
        elif get_app_config("FILTER_BY_POST_FILTER", False):
            request.search.post_filter.must.append(request.args.filter)
        else:
            request.search.query.must.append(request.args.filter)

    return apply_filters


def get_apply_time_limit_filter(setting_name: str) -> SearchFilterFunction:
    """Applies the configured time limit filter based on the resource section"""

    def apply_time_limit_filter(request: NewshubSearchRequest) -> None:
        if request.is_admin:
            return

        limit_days = get_setting(setting_name)
        if limit_days and request.company and not request.company.archive_access:
            request.search.query.filter.append(
                {
                    "range": {
                        "versioncreated": {
                            "gte": f"now-{limit_days}d/d",
                        },
                    },
                }
            )

    return apply_time_limit_filter


async def apply_section_filter(request: NewshubSearchRequest) -> None:
    """Applies section filter(s) based on the resource section"""

    if request.section is None:
        # This should not happen, as it's prefilled by search service
        return

    from newsroom.section_filters import SectionFiltersService

    section_filters = await SectionFiltersService().get_section_filters(request.section.value)

    if not section_filters:
        return

    for s_filter in section_filters:
        if s_filter.query:
            request.search.query.filter.append(query_string_for_section(request.section, s_filter.query))


def apply_company_filter(request: NewshubSearchRequest) -> None:
    """Applies company type filter, based on current company and configured ``COMPANY_TYPES``"""

    if request.is_admin or request.company is None or not request.company.company_type:
        return

    section_type = "agenda" if request.section == SectionEnum.AGENDA else "wire"
    for company_type in get_app_config("COMPANY_TYPES", []):
        if company_type["id"] == request.company.company_type:
            if company_type.get(f"{section_type}_must"):
                request.search.query.filter.append(company_type[f"{section_type}_must"])
            if company_type.get(f"{section_type}_must_not"):
                request.search.query.must_not.append(company_type[f"{section_type}_must_not"])
            break


def apply_products_filter(request: NewshubSearchRequest) -> None:
    """Applies product filter(s) based on the list of products on the request instance"""

    if request.is_admin and not len(request.args.navigation_ids) and not request.args.product_ids:
        # admin will see everything by default
        return
    elif request.section is None:
        # This should not happen, as it's prefilled by search service
        return

    sdesk_product_ids = [product.sd_product_id for product in request.products if product.sd_product_id]
    if sdesk_product_ids:
        request.search.query.should.append({"terms": {"products.code": sdesk_product_ids}})

    for product in request.products:
        if product.query:
            request.search.query.should.append(query_string_for_section(request.section, product.query))


def prefill_args_from_topic(request: NewshubSearchRequest) -> None:
    """Prefills the request args from the topic on the request"""

    topic = request.topic
    if topic is None:
        return

    if topic.query:
        request.args.q = topic.query

    if topic.created_filter:
        if topic.created_filter.created_from:
            request.args.start_date = topic.created_filter.created_from
        if topic.created_filter.created_to:
            request.args.end_date = topic.created_filter.created_to

    if topic.timezone_offset:
        request.args.timezone_offset = topic.timezone_offset

    if topic.filter:
        request.args.filter = topic.filter

    if topic.advanced:
        request.args.advanced = topic.advanced

    if topic.navigation:
        request.args.navigation_ids = topic.navigation


def apply_advanced_search(request: NewshubSearchRequest) -> None:
    """Applies advanced search filter(s) based on the request args"""

    advanced = request.args.advanced
    if advanced is None:
        return

    if not advanced.get("fields") and request.section is not None:
        advanced["fields"] = get_advanced_search_fields(str(request.section.value))

    if not advanced["fields"]:
        return

    if request.section is SectionEnum.AGENDA:
        if "slugline" in advanced["fields"]:
            # Add ``slugline`` field for Planning & Coverages too
            advanced["fields"].extend(["planning_items.slugline", "coverages.slugline"])

        if "headline" in advanced["fields"]:
            # Add ``headline`` field for Planning items too
            advanced["fields"].append("planning_items.headline")

        if "description" in advanced["fields"]:
            # Replace ``description`` alias with appropriate description fields
            advanced["fields"].remove("description")
            advanced["fields"].extend(
                ["definition_short", "definition_long", "description_text", "planning_items.description_text"]
            )

    if advanced.get("all"):
        request.search.query.must.append(
            query_string(
                advanced["all"],
                ElasticDefaultOperator.AND,
                fields=advanced["fields"],
                multimatch_type=ElasticQueryStringType.CROSS_FIELDS,
                analyze_wildcard=True,
            )
        )

    if advanced.get("any"):
        request.search.query.must.append(
            query_string(
                advanced["any"],
                ElasticDefaultOperator.OR,
                fields=advanced["fields"],
                multimatch_type=ElasticQueryStringType.BEST_FIELDS,
                analyze_wildcard=True,
            )
        )

    if advanced.get("exclude"):
        request.search.query.must_not.append(
            query_string(
                advanced["exclude"],
                ElasticDefaultOperator.OR,
                fields=advanced["fields"],
                multimatch_type=ElasticQueryStringType.BEST_FIELDS,
                analyze_wildcard=True,
            )
        )


def get_apply_highlights(filters: list[SearchFilterFunction]) -> SearchFilterFunction:
    """Adds elastic highlight to the search, using the provided filters to build the highlight query"""

    async def apply_highlights(request: NewshubSearchRequest) -> None:
        if not request.args.es_highlight:
            return

        # Create a separate search query object for highlighting settings
        highlights_request = NewshubSearchRequest(
            section=request.section,
            web_request=request.web_request,
            args=request.args.model_copy(),
            current_user=request.current_user,
            is_admin=request.is_admin,
            user=request.user,
            company=request.company,
            search=ESQuery(),
            products=request.products,
        )

        for search_filter in filters:
            response = search_filter(highlights_request)
            if isawaitable(response):
                await response

        field_query = highlights_request.search.query.must or highlights_request.search.query.filter
        try:
            # pop query_string type from the query which breaks the highlighting
            field_query[0]["query_string"].pop("type", None)
            field_query[0]["query_string"].pop("fields", None)
        except KeyError:
            pass

        selected_fields = (request.args.advanced or {}).get("fields", [])
        fields_to_highlight = (
            selected_fields
            if selected_fields
            else [
                "body_html",
                "headline",
                "slugline",
                "description_text",
                "definition_short",
                "name",
                "definition_long",
            ]
        )
        request.search.query.highlight.setdefault("fields", {})
        request.search.query.highlight.update(
            {
                "pre_tags": ['<span class="es-highlight">'],
                "post_tags": ["</span>"],
            }
        )
        for field in fields_to_highlight:
            request.search.query.highlight["fields"][field] = {
                "number_of_fragments": 0,
                "require_field_match": False,
                "highlight_query": {"bool": {"must": field_query}},
            }

    return apply_highlights


def validate_product_ids_arg(request: NewshubSearchRequest[SearchArgsType]) -> None:
    """Validates the products on the request, based on user and company permissions"""

    if not len(request.args.product_ids):
        return

    company_products_with_zero_seats = (
        [product._id for product in request.company.products or [] if not product.seats]
        if request.company is not None
        else []
    )
    user_specific_products = (
        [product._id for product in request.user.products or []] if request.user is not None else []
    )
    allowed_product_ids = set(company_products_with_zero_seats + user_specific_products)
    for product_id in request.args.product_ids:
        if product_id not in allowed_product_ids:
            raise AuthorizationError(
                403, gettext("Your product is not assigned to you or your company."), title=gettext("403. Forbidden")
            )


def validate_request(request: NewshubSearchRequest) -> None:
    """Validates the request args (user, company, section, products)"""

    if not request.is_admin:
        if not request.company:
            raise AuthorizationError(
                403, gettext("User does not belong to a company."), title=gettext("403. Forbidden")
            )
        elif not len(request.products):
            raise AuthorizationError(
                403, gettext("Your company doesn't have any products defined."), title=gettext("403. Forbidden")
            )

        validate_product_ids_arg(request)

        user_sections = get_user_sections(request.user, request.company)
        if request.section is not None and not user_sections.get(str(request.section.value)):
            raise AuthorizationError(
                403, gettext(f"User does not have access to {request.section} section"), title=gettext("403. Forbidden")
            )

    if request.args.page > 1000:
        raise AuthorizationError(400, gettext("Page limit exceeded"), title=gettext("403. Forbidden"))
