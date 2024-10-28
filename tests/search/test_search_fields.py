from urllib.parse import quote
from datetime import datetime

from superdesk.core import json
from tests.utils import get_json
from tests.core.utils import create_entries_for


async def test_wire_search_fields(client, app):
    await create_entries_for(
        "items",
        [
            {
                "_id": "test",
                "headline": "foo",
                "ednote": "bar",
                "guid": "test",
                "type": "text",
                "versioncreated": datetime.utcnow(),
            },
        ],
    )

    data = await get_json(client, "/wire/search?q=foo")
    assert 1 == len(data["_items"])

    data = await get_json(client, "/wire/search?q=bar")
    assert 0 == len(data["_items"])


async def test_wire_search_cross_fields(client, app):
    await create_entries_for(
        "items",
        [
            {
                "_id": "test",
                "guid": "test",
                "headline": "foo",
                "body_html": "bar",
                "type": "text",
                "versioncreated": datetime.utcnow(),
            },
        ],
    )

    data = await get_json(client, "/wire/search?q=foo+bar&default_operator=OR")
    assert 1 == len(data["_items"]), data

    data = await get_json(client, f'/wire/search?advanced={quote(json.dumps({"all": "foo bar"}))}')
    assert 1 == len(data["_items"])

    data = await get_json(client, f'/wire/search?advanced={quote(json.dumps({"any": "foo bar"}))}')
    assert 1 == len(data["_items"])


async def test_agenda_search_fields(client, app):
    await create_entries_for(
        "agenda",
        [
            {"name": "foo", "ednote": "bar", "guid": "test"},
        ],
    )

    data = await get_json(client, "/agenda/search?q=foo")
    assert 1 == len(data["_items"])

    data = await get_json(client, "/agenda/search?q=bar")
    assert 0 == len(data["_items"])
