from flask import json
from ..utils import load_fixture, add_fixture_to_db
from tests import utils


def fix_spaces(input):
    return input.replace("\u202f", " ")


def test_copy_agenda(client, app):
    item = add_fixture_to_db("agenda", "agenda_copy_fixture.json")
    item_id = item["_id"]

    resp = client.post(f"/wire/{item_id}/copy?type=agenda", content_type="application/json")
    data = json.loads(resp.get_data())
    assert resp.status_code == 200

    expected_text = load_fixture("agenda_copy_text.txt")
    assert fix_spaces(data["data"]) == expected_text


def test_copy_wire(client, app):
    item = add_fixture_to_db("items", "item_copy_fixture.json")
    item_id = item["_id"]

    resp = client.post(f"/wire/{item_id}/copy?type=wire", content_type="application/json")
    data = json.loads(resp.get_data())
    assert resp.status_code == 200

    expected_text = load_fixture("item_copy_text.txt")
    assert fix_spaces(data["data"]) == expected_text


def test_copy_agenda_with_restricted_coverage_details(client, app, restrict_user):
    item = add_fixture_to_db("agenda", "agenda_copy_fixture.json")
    item_id = item["_id"]

    utils.login(client, restrict_user)

    resp = client.post(f"/wire/{item_id}/copy?type=agenda", content_type="application/json")
    data = json.loads(resp.get_data())
    assert resp.status_code == 200

    expected_text = load_fixture("agenda_copy_text_2.txt")

    assert fix_spaces(data["data"]) == expected_text
