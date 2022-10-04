Feature: Agenda Search
    Background: Push content
        When we post json to "/push"
        """
        {
            "guid": "event1", "type": "event", "state": "scheduled", "pubstatus": "usable",
            "slugline": "New Press Conference",
            "name": "Prime minister press conference",
            "dates": {
                "start": "2018-05-28T04:00:00+0000",
                "end": "2018-05-28T05:00:00+0000",
                "tz": "Australia/Sydney"
            },
            "calendars": [{"qcode": "cal1", "name": "Calendar1"}],
            "subject": [
                {"code": "d1", "scheme": "sttdepartment", "name": "Dep1"},
                {"code": "s1", "scheme": "sttsubj", "name": "Sub1"},
                {"code": "e1", "scheme": "event_type", "name": "Sports"}
            ],
            "place": [
                {"code": "NSW", "name": "New South Wales"}
            ],
            "anpa_category": [
                {"qcode": "a", "name": "Australian General News"}
            ]
        }
        """
        And we post json to "/push"
        """
        {
            "guid": "plan1", "type": "planning", "state": "scheduled", "pubstatus": "usable",
            "event_item": "event1",
            "slugline": "New Press Conference",
            "name": "Prime minister press conference",
            "planning_date": "2018-05-28T05:00:00+0000",
            "agendas": [
                {"_id": "test", "name": "Agenda1"},
                {"_id": "test", "name": "Agenda2"}
            ],
            "subject": [
                {"code": "d2", "scheme": "sttdepartment", "name": "Dep2"},
                {"code": "s1", "scheme": "sttsubj", "name": "Sub1"},
                {"code": "s2", "scheme": "sttsubj", "name": "Sub2"}
            ],
            "place": [
                {"code": "VIC", "name": "Victoria"}
            ],
            "urgency": 3,
            "anpa_category": [
                {"qcode": "e", "name": "Entertainment"}
            ],
            "coverages": [{
                "coverage_id": "plan1_cov1",
                "firstcreated": "2018-05-28T05:00:00+0000",
                "workflow_status": "draft",
                "planning": {
                    "g2_content_type": "text",
                    "slugline": "Vivid planning item",
                    "internal_note": "internal note here",
                    "genre": [{"name": "Article (news)", "qcode": "Article"}],
                    "ednote": "ed note here",
                    "scheduled": "2018-05-28T10:51:52+0000"
                },
                "news_coverage_status": {
                    "name": "coverage intended",
                    "label": "Planned",
                    "qcode": "ncostat:int"
                }
            }]
        }
        """
        And we post json to "/push"
        """
        {
            "guid": "plan2", "type": "planning", "state": "scheduled", "pubstatus": "usable",
            "event_item": "event1",
            "slugline": "New Press Conference",
            "name": "Prime minister press conference",
            "planning_date": "2018-05-28T05:00:00+0000",
            "agendas": [
                {"_id": "test", "name": "Agenda1"},
                {"_id": "test", "name": "Agenda2"}
            ],
            "subject": [
                {"code": "d3", "scheme": "sttdepartment", "name": "Dep3"},
                {"code": "s1", "scheme": "sttsubj", "name": "Sub1"},
                {"code": "s2", "scheme": "sttsubj", "name": "Sub2"}
            ],
            "place": [
                {"code": "VIC", "name": "Victoria"}
            ],
            "urgency": 3,
            "anpa_category": [
                {"qcode": "e", "name": "Entertainment"}
            ],
            "coverages": [{
                "coverage_id": "plan2_cov1",
                "firstcreated": "2018-05-28T05:00:00+0000",
                "workflow_status": "draft",
                "planning": {
                    "g2_content_type": "photo",
                    "slugline": "Vivid planning item",
                    "internal_note": "internal note here",
                    "genre": [{"name": "Article (news)", "qcode": "Article"}],
                    "ednote": "ed note here",
                    "scheduled": "2018-05-28T10:51:52+0000"
                },
                "news_coverage_status": {
                    "name": "coverage not decided yet",
                    "label": "Not Decided",
                    "qcode": "ncostat:notdec"
                }
            }]
        }
        """
        And we post json to "/push"
        """
        {
            "guid": "plan3", "type": "planning", "state": "scheduled", "pubstatus": "usable",
            "slugline": "New Press Conference",
            "name": "Prime minister press conference",
            "planning_date": "2018-05-28T06:00:00+0000",
            "coverages": [{
                "coverage_id": "plan3_cov1",
                "firstcreated": "2018-05-28T05:00:00+0000",
                "workflow_status": "draft",
                "planning": {
                    "g2_content_type": "text",
                    "slugline": "Vivid planning item",
                    "internal_note": "internal note here",
                    "genre": [{"name": "Article (news)", "qcode": "Article"}],
                    "ednote": "ed note here",
                    "scheduled": "2018-05-28T10:51:52+0000"
                },
                "news_coverage_status": {
                    "name": "coverage intended",
                    "label": "Planned",
                    "qcode": "ncostat:int"
                }
            }]
        }
        """

    @auth @admin
    Scenario: Search Planning Only
        When we get "/agenda/search"
        Then we get the following order
        """
        ["event1", "plan3"]
        """
        When we get "/agenda/search?itemType=events"
        Then we get the following order
        """
        ["event1"]
        """
        When we get "/agenda/search?itemType=planning"
        Then we get the following order
        """
        ["plan1", "plan2", "plan3"]
        """

    @auth @admin @wip
    Scenario: Search Planning with Events
        When we get "/agenda/search"
        Then we get aggregations
        """
        {
            "agendas.agenda": ["Agenda1", "Agenda2"],
            "calendar": ["Calendar1"],
            "place": ["New South Wales", "Victoria"],
            "coverage.coverage_type": ["text", "photo"],
            "urgency": [3],
            "service": ["Australian General News", "Entertainment"],
            "event_type.event_type_filtered.event_type": ["Sports"],
            "sttdepartment.sttdepartment_filtered.sttdepartment": ["Dep1", "Dep2", "Dep3"],
            "sttsubj.sttsubj_filtered.sttsubj": ["Sub1", "Sub2"]
        }
        """
        When we get "/agenda/search?filter={\"sttdepartment\":[\"Dep1\"]}"
        Then we get list with 1 items
        """
        {"_items": [{
            "_id": "event1",
            "_hits": {
                "matched_event": true,
                "matched_planning_items": ["plan1", "plan2"]
            }
        }]}
        """
        When we get "/agenda/search?filter={\"sttdepartment\":[\"Dep2\"]}"
        Then we get list with 1 items
        """
        {"_items": [{
            "_id": "event1",
            "_hits": {
                "matched_event": false,
                "matched_planning_items": ["plan1"]
            }
        }]}
        """
        When we get "/agenda/search?filter={\"sttdepartment\":[\"Dep1\"],\"coverage\":[\"photo\"]}"
        Then we get list with 1 items
        """
        {"_items": [{
            "_id": "event1",
            "_hits": {
                "matched_event": true,
                "matched_planning_items": ["plan2"]
            }
        }]}
        """
