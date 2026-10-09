import pytest
from urllib.parse import quote

from newsroom.agenda.filters import include_planning_items_products, planning_items_query_string

from tests.utils import get_json

ALL_EVENTS = {"code": "all-events", "name": "All Events"}
PLANNING_ITEMS = {"code": "planning-items", "name": "Planning Items"}


@pytest.fixture
def init_agenda_items():
    pass


def get_event(guid: str, name: str, country: str, products: list[dict[str, str]]):
    return {
        "type": "event",
        "guid": guid,
        "event_id": guid,
        "state": "scheduled",
        "pubstatus": "usable",
        "name": name,
        "dates": {"start": "2038-05-28T04:00:00+0000", "end": "2038-05-28T05:00:00+0000", "tz": "America/Toronto"},
        "location": [{"name": country, "qcode": f"{guid}-venue", "address": {"country": country}}],
        "products": products,
        "versioncreated": "2038-05-16T11:24:20+0000",
    }


def get_planning(guid: str, name: str, products: list[dict[str, str]], event_item: str | None = None):
    return {
        "type": "planning",
        "guid": guid,
        "item_id": guid,
        "event_item": event_item,
        "state": "scheduled",
        "pubstatus": "usable",
        "item_class": "plinat:newscoverage",
        "name": name,
        "planning_date": "2038-05-28T04:00:00+0000",
        "agendas": [],
        "coverages": [],
        "products": products,
        "versioncreated": "2038-05-16T11:24:20+0000",
    }


@pytest.fixture
async def agenda_items(client, init_agenda_items):
    items = [
        # events with a linked planning item
        get_event("event-canada", "Town hall on data centres", "Canada", [ALL_EVENTS]),
        get_planning("plan-canada", "Town hall on data centres", [PLANNING_ITEMS], event_item="event-canada"),
        get_event("event-usa", "Tour of data centres", "United States", [ALL_EVENTS]),
        get_planning("plan-usa", "Tour of data centres", [PLANNING_ITEMS], event_item="event-usa"),
        get_event("event-budget", "Budget speech", "Canada", [ALL_EVENTS]),
        get_planning("plan-budget", "Budget speech", [PLANNING_ITEMS], event_item="event-budget"),
        # event without planning items
        get_event("event-only", "Forum on data centres", "United Kingdom", [ALL_EVENTS]),
        # adhoc planning items
        get_planning("plan-adhoc", "Hearing on data centres", [PLANNING_ITEMS]),
        get_planning("plan-adhoc-markets", "Stock markets", [PLANNING_ITEMS]),
    ]

    for item in items:
        resp = await client.post("/push", json=item)
        assert resp.status_code == 200, await resp.get_data(as_text=True)


async def search(client, query: str, item_type: str | None = None) -> list[dict]:
    url = f"/agenda/search?date_from=2038-05-01&q={quote(query)}"
    if item_type:
        url += f"&itemType={item_type}"
    return (await get_json(client, url))["_items"]


async def search_ids(client, query: str, item_type: str | None = None) -> set[str]:
    return {item["_id"] for item in await search(client, query, item_type)}


@pytest.mark.parametrize(
    "query, expected",
    [
        (
            "products.code:planning-items",
            {"event-canada", "event-usa", "event-budget", "plan-adhoc", "plan-adhoc-markets"},
        ),
        (
            'products.name:"Planning Items"',
            {"event-canada", "event-usa", "event-budget", "plan-adhoc", "plan-adhoc-markets"},
        ),
        (
            'products.code:planning-items AND "data centres"',
            {"event-canada", "event-usa", "plan-adhoc"},
        ),
        (
            '(location.address.country:Canada OR products.code:planning-items) AND "data centres"',
            {"event-canada", "event-usa", "plan-adhoc"},
        ),
        (
            'products.code:(planning-items OR unknown) AND "data centres"',
            {"event-canada", "event-usa", "plan-adhoc"},
        ),
        (
            'NOT products.code:planning-items AND "data centres"',
            {"event-only"},
        ),
        (
            "products.code:all-events",
            {"event-canada", "event-usa", "event-budget", "event-only"},
        ),
        (
            "planning_items.products.code:planning-items",
            {"event-canada", "event-usa", "event-budget", "plan-adhoc", "plan-adhoc-markets"},
        ),
    ],
)
async def test_search_by_products_includes_linked_planning_items(client, agenda_items, query, expected):
    assert await search_ids(client, query) == expected


@pytest.mark.parametrize(
    "query",
    [
        "products.code:planning-items",
        'products.code:planning-items AND "data centres"',
        '(location.address.country:Canada OR products.code:planning-items) AND "data centres"',
    ],
)
async def test_search_by_products_hits_include_linked_planning_items(client, agenda_items, query):
    # the client hides items with planning items when none of them is in ``matched_planning_items``
    items = {item["_id"]: item for item in await search(client, query)}
    assert items["event-canada"]["_hits"]["matched_planning_items"] == ["plan-canada"]
    assert items["event-usa"]["_hits"]["matched_planning_items"] == ["plan-usa"]


async def test_search_by_products_events_only(client, agenda_items):
    # products of planning items are not used when searching for events only
    assert await search_ids(client, "products.code:planning-items", item_type="events") == set()
    assert await search_ids(client, "products.code:all-events", item_type="events") == {
        "event-canada",
        "event-usa",
        "event-budget",
        "event-only",
    }


@pytest.mark.parametrize(
    "query, expected",
    [
        ("products.code:abc", "(products.code:abc OR planning_items.products.code:abc)"),
        (
            'products.code:abc AND "data centres"',
            '(products.code:abc OR planning_items.products.code:abc) AND "data centres"',
        ),
        (
            "(location.address.country:Canada OR products.code:abc) AND foo",
            "(location.address.country:Canada OR (products.code:abc OR planning_items.products.code:abc)) AND foo",
        ),
        (
            'products.name:"Planning Items"',
            '(products.name:"Planning Items" OR planning_items.products.name:"Planning Items")',
        ),
        (
            "products.code:(abc OR def)",
            "(products.code:(abc OR def) OR planning_items.products.code:(abc OR def))",
        ),
        ("planning_items.products.code:abc", "planning_items.products.code:abc"),
        ("event.products.code:abc", "event.products.code:abc"),
        ('"data centres"', '"data centres"'),
    ],
)
def test_include_planning_items_products(query, expected):
    assert include_planning_items_products(query) == expected


@pytest.mark.parametrize(
    "query, expected",
    [
        ("products.code:abc", "planning_items.products.code:abc"),
        (
            "slugline:abc AND NOT products.name:def",
            "planning_items.slugline:abc AND NOT planning_items.products.name:def",
        ),
        ("planning_items.products.code:abc", "planning_items.products.code:abc"),
        ("planning_items.slugline:abc", "planning_items.slugline:abc"),
        ("event.slugline:abc", "event.slugline:abc"),
    ],
)
def test_planning_items_query_string_prefixes_nested_fields(query, expected):
    assert planning_items_query_string(query, nested=True)["query_string"]["query"] == expected
