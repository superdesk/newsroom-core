from typing import List, Dict, Any, Optional, Type, TypedDict
import logging
from copy import deepcopy

from newsroom import Resource


class SearchGroupNestedConfig(TypedDict, total=False):
    parent: str
    field: str
    value: str
    include_planning: bool
    searchfield: str


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


def get_nested_config(resource_type: str, field: str) -> Optional[SearchGroupNestedConfig]:
    config = (nested_agg_groups.get(resource_type) or {}).get(field)
    if config is not None:
        return config.get("nested")
    return None


def init_nested_aggregation(resource: Type[Resource], groups: List[SearchGroupConfig], aggs: Dict[str, Any]):
    """Applies aggregation & mapping changes for nested search groups"""

    resource_type = resource.datasource["source"]

    if not len(groups):
        logger.info(f"Resource '{resource_type}': no search groups defined, no need to continue")
        return
    elif not len(resource.SUPPORTED_NESTED_SEARCH_FIELDS):
        logger.warning(f"Resource '{resource_type}': no nested search fields supported")
        return

    agg_groups: Dict[str, Dict[str, List[SearchGroupNestedConfig]]] = {}

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
        agg_groups[nested["parent"]].setdefault(nested["field"], []).append(nested)
        nested.setdefault("searchfield", "name")

        nested_agg_groups[resource_type][field] = group
        group["agg_path"] = f"{field}.{field}_filtered.{field}.buckets"

    for parent, fields in agg_groups.items():
        nested_agg_fields.add(parent)
        for field, configs in fields.items():
            _update_agg_to_nested(parent, field, configs, aggs)


def merge_planning_nested_aggs(aggs: Dict[str, Any]):
    """Merge nested Planning agg buckets to parent agg bucket"""

    def get_buckets(field_aggs: Dict[str, Any], field: str) -> List[Dict[str, Any]]:
        return field_aggs[field][f"{field}_filtered"][field]["buckets"]

    planning_fields = [
        field
        for field, config in nested_agg_groups["agenda"].items()
        if (config.get("nested") or {}).get("include_planning")
    ]

    for field in planning_fields:
        planning_aggs = aggs.pop(f"{field}_planning", None)
        if planning_aggs is None:
            continue

        try:
            field_buckets = get_buckets(aggs, field)
            field_aggs = [bucket["key"] for bucket in field_buckets]
            for bucket in get_buckets(planning_aggs, field):
                if bucket["key"] not in field_aggs:
                    field_buckets.append(bucket)
        except KeyError as e:
            logger.warning(f"Failed to process Planning nested aggs for {field}: key {e} not found")


def merge_planning_aggs(aggs: Dict[str, Any]):
    merge_planning_nested_aggs(aggs)
    for field, planning_aggs in (aggs.get("planning_items") or {}).items():
        field_buckets = (aggs.get(field) or {}).get("buckets")

        if field_buckets is None:
            continue

        field_aggs = [bucket["key"] for bucket in field_buckets]
        for bucket in planning_aggs.get("buckets") or []:
            if bucket["key"] not in field_aggs:
                field_buckets.append(bucket)


def _update_agg_to_nested(
    parent: str,
    field: str,
    configs: List[SearchGroupNestedConfig],
    aggs: Dict[str, Any],
):
    """Updates/Adds aggregations config for ``parent`` and associated ``groups``"""

    if not aggs.get(f"_{parent}"):
        aggs[f"_{parent}"] = deepcopy(aggs.get(parent))

    original_aggs = deepcopy(aggs[f"_{parent}"])

    def set_agg_config(key: str, agg_filter: Dict[str, Any]):
        aggs[key] = {
            "nested": {"path": parent},
            "aggs": {
                f"{key}_filtered": {"filter": agg_filter, "aggs": {key: original_aggs}},
            },
        }

    def set_planning_agg_config(key: str, agg_filter: Dict[str, Any]):
        planning_aggs = deepcopy(original_aggs)
        planning_aggs["terms"]["field"] = "planning_items." + planning_aggs["terms"]["field"]

        aggs[f"{key}_planning"] = {
            "nested": {"path": "planning_items"},
            "aggs": {
                key: {
                    "nested": {"path": f"planning_items.{parent}"},
                    "aggs": {
                        f"{key}_filtered": {
                            "filter": agg_filter,
                            "aggs": {key: planning_aggs},
                        },
                    },
                },
            },
        }

    for config in configs:
        set_agg_config(
            config["value"],
            {"bool": {"filter": [{"term": {f"{parent}.{field}": config["value"]}}]}},
        )
        if config.get("include_planning"):
            set_planning_agg_config(
                config["value"],
                {"bool": {"filter": [{"term": {f"planning_items.{parent}.{field}": config["value"]}}]}},
            )

    set_agg_config(
        parent,
        {"bool": {"must_not": [{"terms": {f"{parent}.{field}": [config["value"] for config in configs]}}]}},
    )
