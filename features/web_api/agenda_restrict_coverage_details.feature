Feature: Agenda Restricted Coverage Details
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
            ],
            "location": [{
                "name": "Sydney Harbour Bridge",
                "address": {
                    "city": "Sydney",
                    "state": "New South Wales",
                    "country": "Australia",
                    "line": ["Hickson Road"],
                    "postal_code": "2000",
                    "type": "attraction",
                    "title": "Sydney Harbour Bridge",
                    "area": "Council of the City of Sydney"
                }
            }]
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
            }, {
                "coverage_id": "plan1_cov2",
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

    Scenario: Search Planning
        Given "companies"
        """
        [{
            "_id": "5e65964bf5db68883df561b0",
            "name": "All Access Co.",
            "is_enabled": true,
            "company_type": "internal"
        }, {
            "_id": "5e65964bf5db68883df561b1",
            "name": "Restricted Access Co.",
            "is_enabled": true,
            "company_type": "public",
            "restrict_coverage_info": true
        }]
        """
        And "users"
        """
        [{
            "_id": "5e65964bf5db68883df561a1",
            "company": "5e65964bf5db68883df561b0",
            "user_type": "administrator",
            "first_name": "admin",
            "last_name": "admin",
            "email": "admin2@sourcefabric.org",
            "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
            "is_validated": true,
            "is_enabled": true,
            "is_approved": true
        }, {
            "_id": "5e65964bf5db68883df561a2",
            "company": "5e65964bf5db68883df561b1",
            "user_type": "administrator",
            "first_name": "admin",
            "last_name": "admin",
            "email": "user1@restricted.org",
            "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
            "is_validated": true,
            "is_enabled": true,
            "is_approved": true
        }]
        """
        When we login with email "admin2@sourcefabric.org" and password "admin"
        When we get "/agenda/search"
        Then we get list with 1 items
        """
        {"_items": [{
            "coverages": [{
                "coverage_id": "plan1_cov1",
                "coverage_type": "text",
                "scheduled": "2018-05-28T10:51:52+0000",
                "slugline": "Vivid planning item",
                "workflow_status": "draft",
                "coverage_status": "coverage intended"
            }, {
                "coverage_id": "plan1_cov2",
                "coverage_type": "text",
                "scheduled": "2018-05-28T10:51:52+0000",
                "slugline": "Vivid planning item",
                "workflow_status": "draft",
                "coverage_status": "coverage intended"
            }],
            "planning_items": [{
                "coverages": [{
                    "coverage_id": "plan1_cov1",
                    "news_coverage_status": {
                        "label": "Planned",
                        "name": "coverage intended",
                        "qcode": "ncostat:int"
                    },
                    "workflow_status": "draft",
                    "planning": {
                        "g2_content_type": "text",
                        "ednote": "ed note here",
                        "internal_note": "internal note here",
                        "scheduled": "2018-05-28T10:51:52+0000",
                        "slugline": "Vivid planning item"
                    }
                }, {
                    "coverage_id": "plan1_cov2",
                    "news_coverage_status": {
                        "label": "Planned",
                        "name": "coverage intended",
                        "qcode": "ncostat:int"
                    },
                    "workflow_status": "draft",
                    "planning": {
                        "g2_content_type": "text",
                        "ednote": "ed note here",
                        "internal_note": "internal note here",
                        "scheduled": "2018-05-28T10:51:52+0000",
                        "slugline": "Vivid planning item"
                    }
                }]
            }]
        }]}
        """
        When we login with email "user1@restricted.org" and password "admin"
        When we get "/agenda/search"
        Then we get list with 1 items
        """
        {"_items": [{
            "coverages": [{
                "coverage_id": "plan1_cov1",
                "coverage_type": "text",
                "scheduled": "__no_value__",
                "slugline": "__no_value__",
                "workflow_status": "__no_value__",
                "coverage_status": "__no_value__"
            }, {
                "coverage_id": "plan1_cov2",
                "coverage_type": "text",
                "scheduled": "__no_value__",
                "slugline": "__no_value__",
                "workflow_status": "__no_value__",
                "coverage_status": "__no_value__"
            }],
            "planning_items": [{
                "coverages": [{
                    "coverage_id": "plan1_cov1",
                    "news_coverage_status": "__no_value__",
                    "workflow_status": "__no_value__",
                    "planning": {
                        "g2_content_type": "text",
                        "ednote": "__no_value__",
                        "internal_note": "__no_value__",
                        "scheduled": "__no_value__",
                        "slugline": "__no_value__"
                    }
                }, {
                    "coverage_id": "plan1_cov2",
                    "news_coverage_status": "__no_value__",
                    "workflow_status": "__no_value__",
                    "planning": {
                        "g2_content_type": "text",
                        "ednote": "__no_value__",
                        "internal_note": "__no_value__",
                        "scheduled": "__no_value__",
                        "slugline": "__no_value__"
                    }
                }]
            }]
        }]}
        """
        When we post json to "/push"
        """
        {
            "guid": "foo",
            "type": "text",
            "headline": "Foo",
            "firstcreated": "2017-11-27T08:00:57+0000",
            "body_html": "<p>foo bar</p>",
            "genre": [{"name": "News", "code": "news"}],
            "event_id": "urn:event/1",
            "coverage_id": "plan1_cov2",
            "subject": [
                {"name": "a", "code": "a", "scheme": "a"},
                {"name": "b", "code": "b", "scheme": "b"}
            ]
        }
        """
        When we get "/agenda/search"
        Then we get list with 1 items
        """
        {"_items": [{
            "coverages": [{
                "coverage_id": "plan1_cov1",
                "coverage_type": "text",
                "scheduled": "__no_value__",
                "slugline": "__no_value__",
                "workflow_status": "__no_value__",
                "coverage_status": "__no_value__"
            }, {
                "coverage_id": "plan1_cov2",
                "coverage_type": "text",
                "scheduled": "2018-05-28T10:51:52+0000",
                "slugline": "Vivid planning item",
                "workflow_status": "completed",
                "coverage_status": "coverage intended",
                "delivery_id": "foo",
                "delivery_href": "/wire/foo"
            }],
            "planning_items": [{
                "coverages": [{
                    "coverage_id": "plan1_cov1",
                    "news_coverage_status": "__no_value__",
                    "workflow_status": "__no_value__",
                    "planning": {
                        "g2_content_type": "text",
                        "ednote": "__no_value__",
                        "internal_note": "__no_value__",
                        "scheduled": "__no_value__",
                        "slugline": "__no_value__"
                    }
                }, {
                    "coverage_id": "plan1_cov2",
                    "news_coverage_status": {
                        "label": "Planned",
                        "name": "coverage intended",
                        "qcode": "ncostat:int"
                    },
                    "workflow_status": "completed",
                    "planning": {
                        "g2_content_type": "text",
                        "ednote": "ed note here",
                        "internal_note": "internal note here",
                        "scheduled": "2018-05-28T10:51:52+0000",
                        "slugline": "Vivid planning item"
                    }
                }]
            }]
        }]}
        """
