from tests.utils import get_json


def test_wire_search_fields(client, app):
    app.data.insert(
        "items",
        [
            {"headline": "foo", "ednote": "bar", "guid": "test", "type": "text"},
        ],
    )

    data = get_json(client, "/wire/search?q=foo")
    assert 1 == len(data["_items"])

    data = get_json(client, "/wire/search?q=bar")
    assert 0 == len(data["_items"])


def test_agenda_search_fields(client, app):
    app.data.insert(
        "agenda",
        [
            {"name": "foo", "ednote": "bar", "guid": "test"},
        ],
    )

    data = get_json(client, "/agenda/search?q=foo")
    assert 1 == len(data["_items"])

    data = get_json(client, "/agenda/search?q=bar")
    assert 0 == len(data["_items"])
