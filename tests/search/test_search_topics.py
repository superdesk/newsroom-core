from flask import json
from unittest.mock import patch
from newsroom.agenda.agenda import AgendaService
from newsroom.wire.search import WireSearchService


def assert_no_aggs(service, search):
    with patch.object(service, "internal_get") as mock_get:
        service.get_items_by_query(search)
        mock_get.assert_called_once()
        req = mock_get.call_args[0][0]
        source = json.loads(req.args.get("source"))
        assert "aggs" not in source


def test_get_topic_query_wire(app):
    with app.app_context():
        service = WireSearchService()
        search = service.get_topic_query(
            {"query": "topic-query"},
            {"user_type": "administrator"},
            None,
            {},
            args={"es_highlight": 1, "ids": ["item-id"]},
        )

        assert search is not None
        assert "bool" in search.query
        assert {"terms": {"_id": ["item-id"]}} in search.query["bool"]["filter"]
        assert "aggs" not in search.query

        assert_no_aggs(service, search)


def test_get_topic_query_agenda(app):
    with app.app_context():
        service = AgendaService()
        search = service.get_topic_query(
            {"query": "topic-query"},
            {"user_type": "administrator"},
            None,
            {},
            args={"es_highlight": 1, "ids": ["item-id"]},
        )

        assert search is not None
        assert "bool" in search.query
        assert {"terms": {"_id": ["item-id"]}} in search.query["bool"]["filter"]
        assert "aggs" not in search.query

        assert_no_aggs(service, search)
