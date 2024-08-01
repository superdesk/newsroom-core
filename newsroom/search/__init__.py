from typing import Dict, List, Literal, TypedDict, Union

from superdesk.flask import render_template
from newsroom.gettext import get_session_locale
from newsroom.email import get_language_template_name


def init_app(app):
    app.add_template_global(render_search_tips_html)


def render_search_tips_html(search_type) -> str:
    locale = (get_session_locale() or "en").lower()
    template_name = get_language_template_name(f"search_tips_{search_type}", locale, "html")

    return render_template(template_name)


class QueryStringParams(TypedDict, total=False):
    query: str
    default_operator: Literal["AND", "OR"]
    analyze_wildcard: bool
    lenient: bool
    fields: List[str]
    type: Literal["cross_fields", "best_fields"]


Value = Union[str, bool, int]


class QueryStringQuery(TypedDict):
    query_string: QueryStringParams


class ExistsQueryParam(TypedDict):
    field: str


class ExistsQuery(TypedDict):
    exists: ExistsQueryParam


class MatchQuery(TypedDict):
    match: Dict[str, Value]


class TermQuery(TypedDict):
    term: Dict[str, Value]


class TermsQuery(TypedDict):
    terms: Dict[str, List[Value]]


class IDsQuery(TypedDict):
    ids: Dict[Literal["values"], List[str]]


class RangeQuery(TypedDict):
    range: Dict[str, Dict[Literal["gte", "gt", "lte", "lt"], Value]]


class BoolQueryParams(TypedDict, total=False):
    must: List["Query"]
    must_not: List["Query"]
    should: List["Query"]
    filter: List["Query"]
    minimum_should_match: int


class BoolQuery(TypedDict):
    bool: BoolQueryParams


class NestedQueryParams(TypedDict):
    path: str
    query: Union[TermQuery, BoolQuery]


class NestedQuery(TypedDict):
    nested: NestedQueryParams


TermLevelQuery = Union[TermQuery, TermsQuery, IDsQuery, ExistsQuery, RangeQuery]
FullTextQuery = Union[QueryStringQuery, MatchQuery]
Query = Union[TermLevelQuery, FullTextQuery, BoolQuery, NestedQuery]
