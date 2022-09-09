from typing import List, Dict, Any, Type, TypedDict
import logging
from copy import deepcopy

from newsroom import Resource


class SearchGroupNestedConfig(TypedDict):
    parent: str
    field: str
    value: str


class SearchGroupConfig(TypedDict, total=False):
    field: str
    label: str
    nested: SearchGroupNestedConfig
    agg_path: str  # Generated on startup, used to retrieve agg value from buckets


logger = logging.getLogger(__name__)
nested_agg_groups: Dict[str, Dict[str, SearchGroupConfig]] = {}
nested_agg_fields = set()


def is_search_field_nested(resource_type: str, field: str):
    """Returns ``True`` if the ``resource_type`` is configured for nested search group"""

    return field in (nested_agg_groups.get(resource_type) or {}) or field in nested_agg_fields


def init_nested_aggregation(
    resource: Type[Resource],
    groups: List[SearchGroupConfig],
    aggregations: Dict[str, Any]
):
    """Applies aggregation & mapping changes for nested search groups"""

    resource_type = resource.datasource["source"]

    if not len(groups):
        logger.info(f"Resource '{resource_type}': no search groups defined, no need to continue")
        return
    elif not len(resource.SUPPORTED_NESTED_SEARCH_FIELDS):
        logger.warning(f"Resource '{resource_type}': no nested search fields supported")
        return

    agg_groups: Dict[str, Dict[str, Any]] = {}

    nested_agg_groups[resource_type] = {}

    for group in groups:
        field = group.get("field")
        nested = group.get("nested")
        if field is None or nested is None:
            # Invalid group config or no nesting is enabled on this group
            continue
        elif not nested.get("field") or not nested.get("parent") or not nested.get("value"):
            logger.warning(f"Resource '{resource_type}' search group '{field}': incorrectly configured")
            continue
        elif nested["parent"] not in resource.SUPPORTED_NESTED_SEARCH_FIELDS:
            logger.warning(f"Resource '{resource_type}' search group '{field}': nesting not supported")
            continue

        agg_groups.setdefault(nested["parent"], {})
        agg_groups[nested["parent"]].setdefault(nested["field"], []).append(nested["value"])

        nested_agg_groups[resource_type][field] = group
        group["agg_path"] = f"{field}.{field}_filtered.{field}.buckets"

    for parent, fields in agg_groups.items():
        nested_agg_fields.add(parent)
        for field, values in fields.items():
            _update_agg_to_nested(parent, field, values, aggregations)


def _update_agg_to_nested(parent: str, field: str, groups: List[str], aggregations: Dict[str, Any]):
    """Updates/Adds aggregations config for ``parent`` and associated ``groups``"""

    original_aggs = deepcopy(aggregations[parent])

    def set_agg_config(key: str, filter: Dict[str, Any]):
        aggregations[key] = {
            "nested": {"path": parent},
            "aggs": {
                f"{key}_filtered": {
                    "filter": filter,
                    "aggs": {key: original_aggs}
                },
            },
        }

    for group in groups:
        set_agg_config(group, {"bool": {"must": [{"term": {f"{parent}.{field}": group}}]}})

    set_agg_config(parent, {"bool": {"must_not": [{"terms": {f"{parent}.{field}": groups}}]}})
