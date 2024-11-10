from quart import json

from .utils import create_entries_for
from ..utils import load_fixture, load_json_fixture


def fix_spaces(input):
    return input.replace("\u202f", " ")


async def test_copy_agenda(client, app):
    item = load_json_fixture("agenda_copy_fixture.json")
    await create_entries_for("agenda", [item])
    # item = add_fixture_to_db("agenda", "agenda_copy_fixture.json")
    item_id = item["_id"]

    resp = await client.post(f"/wire/{item_id}/copy?type=agenda")
    data = json.loads(await resp.get_data())
    assert resp.status_code == 200

    expected_text = load_fixture("agenda_copy_text.txt")
    assert fix_spaces(data["data"]) == expected_text


async def test_copy_wire(client, app):
    item = load_json_fixture("item_copy_fixture.json")
    await create_entries_for("items", [item])
    # item = add_fixture_to_db("items", "item_copy_fixture.json")
    item_id = item["_id"]

    resp = await client.post(f"/wire/{item_id}/copy?type=wire")
    data = json.loads(await resp.get_data())
    assert resp.status_code == 200

    expected_text = load_fixture("item_copy_text.txt")
    assert fix_spaces(data["data"]) == expected_text
