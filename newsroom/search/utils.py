from superdesk.core import get_app_config

from newsroom.types import SectionEnum
from .types import QueryStringQuery, ElasticDefaultOperator, ElasticQueryStringType
from .config import SearchGroupNestedConfig


def query_string(
    query: str,
    default_operator: ElasticDefaultOperator = ElasticDefaultOperator.AND,
    fields: list[str] | None = None,
    multimatch_type: ElasticQueryStringType = ElasticQueryStringType.CROSS_FIELDS,
    analyze_wildcard: bool = False,
) -> QueryStringQuery:
    query_string_params = get_app_config("ELASTICSEARCH_QUERY_STRING_DEFAULT_PARAMS", {}).copy()

    query_string_params.update(
        dict(
            query=query,
            default_operator=default_operator,
            lenient=True,
            fields=fields if fields is not None else ["*"],
            type=multimatch_type,
            # We only set ``analyze_wildcard`` if the default is turned off
            # otherwise if default is turned on, then we always set it to True
            analyze_wildcard=query_string_params.get("analyze_wildcard") or analyze_wildcard,
        )
    )

    return dict(query_string=query_string_params)


def query_string_for_section(
    section: SectionEnum, query: str, default_operator: ElasticDefaultOperator = ElasticDefaultOperator.AND
) -> QueryStringQuery:
    fields_config_key = "WIRE_SEARCH_FIELDS" if section == SectionEnum.WIRE else "AGENDA_SEARCH_FIELDS"
    fields = get_app_config(fields_config_key, ["*"])
    return query_string(query, default_operator=default_operator, fields=fields)


def get_filter_query(key: str, val: list[str], aggregation_field: str, nested_config: SearchGroupNestedConfig | None):
    if nested_config:
        return {
            "nested": {
                "path": nested_config["parent"],
                "query": {
                    "bool": {
                        "filter": [
                            {"term": {f"{nested_config['parent']}.{nested_config['field']}": nested_config["value"]}},
                            {"terms": {f"{nested_config['parent']}.{nested_config['searchfield']}": val}},
                        ],
                    },
                },
            },
        }
    return {"terms": {aggregation_field: val}}
