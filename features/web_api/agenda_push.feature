Feature: Agenda Push
    @auth @admin
    Scenario: Push Planning & Event
        When we post json to "/push"
        """
        {
            "guid": "plan1", "type": "planning", "state": "scheduled", "pubstatus": "usable",
            "slugline": "New Press Conference",
            "name": "Prime minister press conference",
            "planning_date": "2018-05-28T05:00:00+0000",
            "coverages": [{
                "coverage_id": "plan1_cov1",
                "firstcreated": "2018-05-28T05:00:00+0000",
                "workflow_status": "draft",
                "planning": {
                    "g2_content_type": "text",
                    "slugline": "Vivid planning item",
                    "internal_note": "internal note here",
                    "genre": [
                        {
                            "name": "Article (news)",
                            "qcode": "Article"
                        }
                    ],
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
        Then we get OK response
        When we post json to "/push"
        """
        {
            "guid": "event1", "type": "event", "state": "scheduled", "pubstatus": "usable",
            "slugline": "New Press Conference",
            "name": "Prime minister press conference",
            "dates": {
                "start": "2018-05-28T03:00:00+0000",
                "end": "2018-05-28T04:00:00+0000",
                "tz": "Australia/Sydney"
            },
            "plans": ["plan1"]
        }
        """
        Then we get OK response
        When we get "/agenda/plan1?format=json"
        Then we get existing resource
        """
        {
            "_id": "plan1", "guid": "plan1",
            "item_type": "planning", "event_id": "event1",
            "display_dates": [{"date": "2018-05-28T10:51:52+0000"}],
            "coverages": [{
                "coverage_id": "plan1_cov1",
                "coverage_type": "text",
                "scheduled": "2018-05-28T10:51:52+0000"
            }],
            "planning_items": [{
                "_id": "plan1",
                "planning_date": "2018-05-28T05:00:00+0000",
                "coverages": [{
                    "coverage_id": "plan1_cov1",
                    "planning": {"scheduled": "2018-05-28T10:51:52+0000"}
                }]
            }]
        }
        """
        When we get "/agenda/event1?format=json"
        Then we get existing resource
        """
        {
            "_id": "event1", "guid": "event1",
            "item_type": "event", "event_id": "event1",
            "display_dates": [{"date": "2018-05-28T10:51:52+0000"}],
            "coverages": [{
                "coverage_id": "plan1_cov1",
                "coverage_type": "text",
                "scheduled": "2018-05-28T10:51:52+0000"
            }],
            "planning_items": [{
                "_id": "plan1",
                "planning_date": "2018-05-28T05:00:00+0000",
                "coverages": [{
                    "coverage_id": "plan1_cov1",
                    "planning": {"scheduled": "2018-05-28T10:51:52+0000"}
                }]
            }]
        }
        """
