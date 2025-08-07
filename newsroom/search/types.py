from typing import Literal, Any, TypeVar, Generic, Callable, Awaitable
from typing_extensions import TypedDict
from dataclasses import dataclass, field
from enum import Enum, unique
import math

from pydantic import Field, AliasChoices, field_validator, model_validator
from quart_babel import gettext

from superdesk.core.types import ProjectedFieldArg, Request, SearchRequest, SortListParam, ESQuery
from superdesk.core import json
from superdesk.core.resources import BaseModel
from superdesk.core.resources.fields import ObjectId
from content_api.errors import BadParameterValueError

from newsroom.types import (
    UserResourceModel,
    CompanyResource,
    SectionEnum,
    ProductResourceModel,
    TopicResourceModel,
    AdvancedSearchParams,
)


# TODO-ASYNC: Review what types are no longer needed after Agenda is migrated to async
@unique
class ElasticDefaultOperator(str, Enum):
    AND = "AND"
    OR = "OR"


@unique
class ElasticQueryStringType(str, Enum):
    CROSS_FIELDS = "cross_fields"
    BEST_FIELDS = "best_fields"


@unique
class ElasticRangeType(str, Enum):
    GREATER_THAN_OR_EQUAL = "gte"
    GREATER_THAN = "gt"
    LESS_THAN_OR_EQUAL = "lte"
    LESS_THAN = "lt"


@unique
class AgendaItemType(str, Enum):
    EVENTS = "events"
    PLANNING = "planning"


class QueryStringParams(TypedDict, total=False):
    query: str
    default_operator: ElasticDefaultOperator
    analyze_wildcard: bool
    lenient: bool
    fields: list[str]
    type: ElasticQueryStringType


Value = str | bool | int


class QueryStringQuery(TypedDict):
    query_string: QueryStringParams


class ExistsQueryParam(TypedDict):
    field: str


class ExistsQuery(TypedDict):
    exists: ExistsQueryParam


class MatchQuery(TypedDict):
    match: dict[str, Value]


class TermQuery(TypedDict):
    term: dict[str, Value]


class TermsQuery(TypedDict):
    terms: dict[str, list[Value]]


class IDsQuery(TypedDict):
    ids: dict[Literal["values"], list[str]]


class RangeQuery(TypedDict):
    range: dict[str, dict[ElasticRangeType, Value]]


class BoolQueryParams(TypedDict, total=False):
    must: list["Query"]
    must_not: list["Query"]
    should: list["Query"]
    filter: list["Query"]
    minimum_should_match: int


class BoolQuery(TypedDict):
    bool: BoolQueryParams


class NestedQueryParams(TypedDict):
    path: str
    query: TermQuery | BoolQuery


class NestedQuery(TypedDict):
    nested: NestedQueryParams


TermLevelQuery = TermQuery | TermsQuery | IDsQuery | ExistsQuery | RangeQuery
FullTextQuery = QueryStringQuery | MatchQuery
Query = TermLevelQuery | FullTextQuery | BoolQuery | NestedQuery


class SearchArgs(TypedDict, total=False):
    q: str
    id: str
    ids: list[str]
    size: int
    bookmarks: str
    ignore_latest: bool
    filter: dict[str, str] | str


class SearchQuery:
    """Class for storing the search parameters for validation and query generation"""

    def __init__(self):
        self.user: UserResourceModel | None = None
        self.company: CompanyResource | None = None
        self.is_admin: bool = False
        self.section: SectionEnum | None = None
        self.navigation_ids: list[ObjectId] = []
        self.products: list[ObjectId] = []
        self.requested_products: list[ObjectId] = []
        self.advanced: AdvancedSearchParams | None = None
        self.args: SearchArgs = {}
        self.lookup: dict[str, Any] = {}
        self.projections: ProjectedFieldArg = {}
        self.request: Request | None = None
        self.aggs: dict[str, Any] | None = None
        self.source: dict[str, Any] = {}
        self.query: BoolQuery = {"bool": {"filter": [], "must": [], "must_not": [], "should": []}}
        self.highlight: dict[str, Any] | None = None
        self.item_type: AgendaItemType | None = None
        self.planning_items_should: list[dict[str, Any]] = []
        self.request_args: SearchRequest = SearchRequest()


class BaseSearchRequestArgs(BaseModel):
    """Common search arguments supported across the various resource types"""

    #: The sorting that should be applied to this request
    sort: SortListParam = [("versioncreated", -1)]

    #: The ID of a user to run this search request for (only available to admin users)
    user_id: ObjectId | None = Field(validation_alias=AliasChoices("user_id", "user"), default=None)

    #: Filter items from this date onwards (an alias for ``created_from``)
    start_date: str | None = Field(
        validation_alias=AliasChoices("start_date", "created_from", "date_from"), default=None
    )

    #: Start time to use with the ``start_date`` argument (defaults to ``00.00:00``)
    start_time: str = Field(validation_alias=AliasChoices("start_time", "created_from_time"), default="00:00:00")

    #: Filter items up to this date (an alias for ``created_to``)
    end_date: str | None = Field(validation_alias=AliasChoices("end_date", "created_to", "date_to"), default=None)

    #: End time to use with the ``end_date`` argument (defaults to ``23:59:59``)
    end_time: str = Field(validation_alias=AliasChoices("end_time", "created_to_time"), default="23:59:59")

    #: Pagination, the number of items to return per page
    page_size: int = Field(validation_alias=AliasChoices("page_size", "size", "max_results"), default=25)

    #: Pagination, the page number to return
    page: int = 0

    #: Pagination, the item number to return from - internally is converted to a page number
    from_item_number: int | None = Field(alias="from", default=None)

    #: An elasticsearch query_string to be added to the filter
    q: str | None = None

    #: The elasticsearch query_string default oeprator, defaults to ``AND``
    default_operator: ElasticDefaultOperator = ElasticDefaultOperator.AND

    #: List of filters to be applied to this request
    filter: dict[str, Any] | None = None

    #: List of item IDs to search for
    ids: list[str] = Field(validation_alias=AliasChoices("ids", "id"), default_factory=list)

    #: The timezone offset, used when constructing the date queries
    timezone_offset: int | None = None

    #: List of Product IDs to use when filtering
    product_ids: list[ObjectId] = Field(
        validation_alias=AliasChoices("product_ids", "products", "product"), default_factory=list
    )

    #: List of Topic IDs (aka Navigation) to use when filtering
    navigation_ids: list[ObjectId] = Field(
        default_factory=list, validation_alias=AliasChoices("navigation_ids", "navigation")
    )

    #: Advanced search params
    advanced: AdvancedSearchParams | None = None

    #: Projection, used to control what fields will be returned
    projection: ProjectedFieldArg | None = None

    #: If ``True``, will tell Elasticsearch to highlight our search results
    es_highlight: bool = False

    #: If ``True``, will include aggregations in the response
    aggs: bool = True

    #: List of User IDs to search for, who has bookmarked items
    bookmarks: list[ObjectId] = Field(default_factory=list)

    @field_validator("filter", mode="before")
    @classmethod
    def parse_filter(cls, value: dict[str, Any] | str | None) -> dict[str, Any] | None:
        """Attempts to convert the filter argument from a string into a dictionary"""

        try:
            return json.loads(value) if isinstance(value, str) else value
        except (ValueError, TypeError):
            raise BadParameterValueError(gettext("Incorrect type supplied for filter parameter"))

    @field_validator("product_ids", "bookmarks", "navigation_ids", "ids", mode="before")
    @classmethod
    def parse_list_ids(cls, value: list[str] | list[ObjectId] | str | ObjectId | None) -> list[str]:
        """If value is not a list, then convert it to a list here

        No need to convert from string to ObjectId, as the underlying field type will do that for us
        and raise the appropriate validation error there
        """

        if not value:
            return []
        elif isinstance(value, (str, ObjectId)):
            return [str(value)]
        return value

    @field_validator("advanced", mode="before")
    @classmethod
    def parse_advanced(cls, value: AdvancedSearchParams | str | None) -> AdvancedSearchParams | None:
        """Attempts to convert the advanced argument from a string into a AdvancedSearchParams instance"""

        try:
            return json.loads(value) if isinstance(value, str) else value
        except (ValueError, TypeError):
            raise BadParameterValueError(gettext("Incorrect type supplied for advanced search params"))

    @field_validator("sort", mode="before")
    @classmethod
    def parse_sort(cls, value: SortListParam | str) -> SortListParam:
        """Tries to extract the sort params from the supplied string:

        Formats Supported:
        python: list[tuple[str, Literal[1, -1]]]
            sort=[("versioncreated", -1)]
        strings: comma separated list, with each entry in one of the following formats
            "{field}:desc"
            "{field}:asc"
            "{field}:-1"
            "{field}:1"
            "{field}"  # ascending order
            "-{field}" # descending order
        """

        # Next try a comma separated list of key:value pairs
        def parse_field(field_spec: str) -> tuple[str, Literal[1, -1]]:
            try:
                field, direction = field_spec.split(":")
            except ValueError:
                # We also support providing just the field name
                # If name is prefixed with `-`, then sort in descending order
                # otherwise defaults to sort in ascending order
                if field_spec[0] == "-":
                    field = field_spec[1:]
                    direction = "desc"
                else:
                    field = field_spec
                    direction = "asc"

            direction_int: Literal[1, -1]
            if direction in ["desc", "asc"]:
                direction_int = -1 if direction == "desc" else 1
            else:
                try:
                    if int(direction) >= 1:
                        direction_int = 1
                    else:
                        direction_int = -1
                except ValueError:
                    raise BadParameterValueError(gettext("Invalid sort param"))

            return field, direction_int

        values = value.split(",") if isinstance(value, str) else value

        return list(filter(None, [parse_field(field.strip()) for field in values]))

    @field_validator("projection", mode="before")
    @classmethod
    def parse_projection(cls, value: ProjectedFieldArg | str | None) -> ProjectedFieldArg | None:
        """Attempts to convert the projection argument from a string to a ProjectedFieldArg instance"""

        try:
            return json.loads(value) if isinstance(value, str) else value
        except (ValueError, TypeError):
            raise BadParameterValueError(gettext("Incorrect type supplied for projection parameter"))

    @model_validator(mode="after")
    def parse_model(self):
        if self.from_item_number is not None:
            # Convert the ``from`` search argument to a page number
            self.page = (math.floor(self.from_item_number / self.page_size) + 1) if self.page_size > 0 else 0
        return self


SearchArgsType = TypeVar("SearchArgsType", bound=BaseSearchRequestArgs)


@dataclass
class NewshubSearchRequest(Generic[SearchArgsType]):
    """Base internal search request instance"""

    #: The search arguments for the query
    args: SearchArgsType = field(default_factory=BaseSearchRequestArgs)

    #: The section the resource belongs to
    section: SectionEnum | None = None

    #: An instance of the web Request, if any
    web_request: Request | None = None

    #: The current user, if any
    current_user: UserResourceModel | None = None

    #: If the current user is an administrator
    is_admin: bool = False

    #: The user this search request is for, if any
    user: UserResourceModel | None = None

    #: The company of the user this search request is for, if any
    company: CompanyResource | None = None

    search: ESQuery = field(default_factory=ESQuery)

    #: The list of pre-filled products to use when constructing the elasticsearch query
    products: list[ProductResourceModel] = field(default_factory=list)

    #: The list of topics to use when constructing the elasticsearch query
    topic: TopicResourceModel | None = None

    #: Match also updated items
    include_updated: bool | None = None


#: Function callable type for use with search filters
SearchFilterFunction = Callable[[NewshubSearchRequest], Awaitable[None] | None]
