from typing import List, Dict, Any, KeysView, Type
import logging
from copy import deepcopy

from superdesk.resource import not_analyzed
from newsroom.factory.app import BaseNewsroomApp
from newsroom import Resource


logger = logging.getLogger(__name__)
nested_agg_groups = {}


def is_search_field_nested(resource_type: str, field: str):
    """Returns ``True`` if the ``resource_type`` is configured for nested search group"""

    return field in (nested_agg_groups.get(resource_type) or {})


def init_nested_aggregation(
    current_app: BaseNewsroomApp,
    resource: Type[Resource],
    groups: List[Dict[str, Any]],
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

    if nested_agg_groups.get(resource_type) is None:
        nested_agg_groups[resource_type] = {}

    for group in groups:
        field = group.get("field")
        nested = group.get("nested")
        if nested is None:
            # No nesting is not enabled on this group
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
        _adjust_es_mapping(current_app, resource_type, parent, fields.keys())
        for field, values in fields.items():
            _update_agg_to_nested(parent, field, values, aggregations)


def _adjust_es_mapping(current_app: BaseNewsroomApp, resource_type: str, parent: str, fields: KeysView[str]):
    """Updates the ES mapping for ``parent``"""

    try:
        original = deepcopy(current_app.config["DOMAIN"][resource_type]["schema"])
    except KeyError:
        logger.warning(f"Resource {resource_type}: original schema not found")
        original = {}

    new_schema: Dict[str, Any] = {
        "type": "nested",
        # Flatten the field in the parent object too
        # This is so non-nested queries/aggregations still work
        # (such as in existing Topics)
        "include_in_parent": True,
        "properties": (original.get("mapping") or {}).get("properties") or {
            "qcode": not_analyzed,
            "name": not_analyzed,
            "scheme": not_analyzed,
        }
    }

    # Make sure all required fields have `not_analyzed`
    # so filtering etc works
    for field in fields:
        if field not in new_schema["properties"].keys():
            new_schema["properties"][field] = not_analyzed

    current_app.config["DOMAIN"][resource_type]["schema"][parent]["mapping"] = new_schema


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
