from flask import render_template
from typing import Dict, List, Literal, TypedDict, Union

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


class TermQueryParams(TypedDict):
    value: str


class TermsQueryParams(TypedDict):
    value: List[str]


TermQuery = Dict[Literal["term"], Dict[str, TermQueryParams]]
TermsQuery = Dict[Literal["terms"], Dict[str, TermsQueryParams]]
MatchQuery = Dict[Literal["match"], Dict[str, str]]
QueryStringQuery = Dict[Literal["query_string"], QueryStringParams]


class BoolQueryParams(TypedDict, total=False):
    must: List["Query"]
    must_not: List["Query"]
    should: List["Query"]
    filter: List["Query"]
    minimum_should_match: int


BoolQuery = Dict[Literal["bool"], BoolQueryParams]


class _NestedQuery(TypedDict):
    path: str
    query: Union[TermQuery, BoolQuery]


NestedQuery = Dict[Literal["nested"], _NestedQuery]

TermLevelQuery = Union[TermQuery, TermsQuery]
FullTextQuery = Union[QueryStringQuery, MatchQuery]
Query = Union[TermLevelQuery, FullTextQuery, BoolQuery, NestedQuery]
