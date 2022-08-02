from newsroom.agenda.agenda import AgendaResource, init_nested_aggregations
from newsroom.agenda.agenda import aggregations
from pprint import pprint


def test_default_agenda_groups_config(app):
    assert app.config["DOMAIN"]["agenda"]["schema"]["subject"]["mapping"]["type"] == "object"
    assert len(app.config["AGENDA_GROUPS"]) == 4

    group_fields = [
        group.get("field")
        for group in app.config["AGENDA_GROUPS"]
    ]
    assert "service" in group_fields
    assert "subject" in group_fields
    assert "urgency" in group_fields
    assert "place" in group_fields

    assert aggregations["subject"]["terms"]["field"] == "subject.name"
    assert "nested" not in aggregations["subject"]


def test_custom_agenda_groups_config(app):
    app.config["AGENDA_GROUPS"].append({
        "field": "event_type",
        "label": "Event Type",
        "nested": {
            "parent": "subject",
            "field": "scheme",
            "value": "event_type",
        },
    })
    init_nested_aggregations(app.config["AGENDA_GROUPS"])

    # Test ``event_type`` was added to ``AGENDA_GROUPS``
    assert len(app.config["AGENDA_GROUPS"]) == 5
    assert "event_type" in [group["field"] for group in app.config["AGENDA_GROUPS"]]

    # Test if the Eve & aggregations config has been updated
    assert app.config["DOMAIN"]["agenda"]["schema"]["subject"]["mapping"]["type"] == "nested"
    assert "terms" not in aggregations["subject"]
    assert aggregations["subject"]["nested"]["path"] == "subject"
