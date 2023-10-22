from flask import json
from ..utils import load_fixture, add_fixture_to_db


def test_copy_agenda(client, app):
    item = add_fixture_to_db("agenda", "agenda_copy_fixture.json")
    item_id = item["_id"]

    resp = client.post(f"/wire/{item_id}/copy?type=agenda", content_type="application/json")
    data = json.loads(resp.get_data())
    assert resp.status_code == 200

    expected_text = load_fixture("agenda_copy_text.txt")
    assert data["data"].replace("\u202F", " ") == expected_text


def test_copy_wire(client, app):
    item = add_fixture_to_db("items", "item_copy_fixture.json")
    item_id = item["_id"]

    resp = client.post(f"/wire/{item_id}/copy?type=wire", content_type="application/json")
    data = json.loads(resp.get_data())
    assert resp.status_code == 200

    expected_text = load_fixture("item_copy_text.txt")
    assert data["data"].replace("\u202F", " ") == expected_text
