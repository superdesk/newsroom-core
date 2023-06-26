from typing import List, Dict, Optional, Any
from copy import deepcopy

from flask import json
from eve.utils import ParsedRequest

from superdesk import get_resource_service
from superdesk.lock import lock, unlock

from newsroom.search.config import nested_agg_groups, SearchGroupNestedConfig
from .manager import manager


@manager.command
def fix_topic_nested_filters():
    """Fix My/Company Topics after adding ``Nested Agg`` to Wire/Agenda group configs

    Previously ``subject`` was used to provide a filter for all custom subjects (such as CPs ``distribution``).
    After removing ``subject`` from ``WIRE_GROUPS`` config, Topics will need to be updated to reflect this change.
    This command will move the ``subject`` filter values into their newly configured ``Nested Agg` group.

    Example:
    ::

        $ python manage.py fix_topic_nested_filters
    """

    lock_name = "fix_topic_nested_filters"

    if not lock(lock_name, expire=1800):
        return

    try:
        group_configs = _get_nested_search_group_configs()
        topics_service = get_resource_service("topics")

        search_value_to_nested_group: Dict[str, str] = {}
        skip_search_values = set()
        for parent_field, search_fields in group_configs.items():
            for saved_topic in topics_service.find(where={f"filter.{parent_field}.0": {"$exists": True}}):
                topic_filters = deepcopy(saved_topic["filter"])
                update_filters = False
                for search_field, search_config in search_fields.items():
                    for search_value in saved_topic["filter"][parent_field]:
                        if search_value in skip_search_values:
                            continue
                        elif search_value in search_value_to_nested_group:
                            nested_group = search_value_to_nested_group[search_value]
                        else:
                            nested_group = _get_attribute_value_from_name(search_config, search_value)
                            if not nested_group:
                                group_field = search_config["field"]
                                print(f"Failed to find {parent_field}.{group_field} using name='{search_value}'")
                                continue

                            if nested_group in search_fields.keys():
                                search_value_to_nested_group[search_value] = nested_group
                            else:
                                skip_search_values.add(search_value)
                                continue

                        update_filters = True
                        topic_filters.setdefault(nested_group, [])
                        if search_value not in topic_filters[nested_group]:
                            topic_filters[nested_group].append(search_value)
                        topic_filters[parent_field] = [
                            value for value in topic_filters[parent_field] if value != search_value
                        ]

                if update_filters:
                    if not len(topic_filters[parent_field]):
                        topic_filters.pop(parent_field, None)
                    topics_service.patch(id=saved_topic["_id"], updates={"filter": topic_filters})
    finally:
        unlock(lock_name)


def _get_nested_search_group_configs() -> Dict[str, Dict[str, SearchGroupNestedConfig]]:
    """
    Returns the ``SearchGroupNestedConfig`` grouped by their parent field and search term

    Example response:
    ::

        {
            "subject": {
                "distribution": {
                    "field": "scheme",
                    "parent": "subject",
                    "value": "distribution",
                },
                "subject_custom": {
                    "field": "scheme",
                    "parent": "subject",
                    "value": "subject_custom",
                },
            },
        }
    """

    configs: Dict[str, Dict[str, SearchGroupNestedConfig]] = {}
    for resource_type, fields_map in nested_agg_groups.items():
        for group in fields_map.values():
            nested = group["nested"]
            if nested["parent"] not in configs:
                configs[nested["parent"]] = {}
            configs[nested["parent"]][group["field"]] = nested
    return configs


def _get_attribute_value_from_name(search_config: SearchGroupNestedConfig, search_value: str) -> Optional[str]:
    """Attempts to retrieve the ``nested.value`` given a ``SearchGroupNestedConfig`` and a filter value"""

    parent_field = search_config["parent"]
    group_field = search_config["field"]

    def _search_items(resource: str):
        req = ParsedRequest()
        req.args = {
            "source": json.dumps({"query": {"bool": {"filter": [{"term": {f"{parent_field}.name": search_value}}]}}}),
            "size": 1,
        }
        response = get_resource_service(resource).internal_get(req=req, lookup={})

        if not response.count():
            return None

        values: List[Dict[str, Any]] = response[0].get(parent_field) or []
        value: Dict[str, Any] = next((s for s in values if s["name"] == search_value), {})
        return value.get(group_field)

    return _search_items("wire_search") or _search_items("agenda") or None
