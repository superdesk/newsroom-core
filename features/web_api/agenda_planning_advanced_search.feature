Feature: Agenda Planning Advanced Search
    Background: Push planning
        When we post json to "/push"
        """
        {
            "guid": "weather-today-sydney", "type": "planning", "state": "scheduled", "pubstatus": "usable",
            "slugline": "current-weather-today",
            "name": "Sydney Australia Weather Today Current",
            "description_text": "<p><h1>Current Sydney Weather Report for Today</h1></p>",
            "planning_date": "2032-05-28T05:00:00+0000",
            "coverages": [{
                "coverage_id": "plan1_cov1",
                "firstcreated": "2018-05-28T05:00:00+0000",
                "workflow_status": "draft",
                "planning": {
                    "g2_content_type": "text",
                    "slugline": "current-weather-today-text",
                    "genre": [{"name": "Article (news)", "qcode": "Article"}],
                    "scheduled": "2032-05-28T05:00:00+0000"
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
            "guid": "weather-today-prague", "type": "planning", "state": "scheduled", "pubstatus": "usable",
            "slugline": "current-weather-today",
            "name": "Prague Weather Today",
            "description_text": "<p><h1>Current Prague Weather Report for Today</h1></p>",
            "planning_date": "2032-05-28T06:00:00+0000",
            "coverages": [{
                "coverage_id": "plan2_cov1",
                "firstcreated": "2018-05-28T05:00:00+0000",
                "workflow_status": "draft",
                "planning": {
                    "g2_content_type": "text",
                    "slugline": "current-weather-today-story",
                    "genre": [{"name": "Article (news)", "qcode": "Article"}],
                    "scheduled": "2032-05-28T06:00:00+0000"
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
            "guid": "weather-today-belgrade", "type": "planning", "state": "scheduled", "pubstatus": "usable",
            "slugline": "current-weather-today",
            "name": "Belgrade Weather Today",
            "description_text": "<p><h1>Current Belgrade Weather Report for Today</h1></p>",
            "planning_date": "2032-05-28T07:00:00+0000",
            "coverages": [{
                "coverage_id": "plan3_cov1",
                "firstcreated": "2018-05-28T05:00:00+0000",
                "workflow_status": "draft",
                "planning": {
                    "g2_content_type": "text",
                    "slugline": "current-weather-today-sidebar",
                    "genre": [{"name": "Article (news)", "qcode": "Article"}],
                    "scheduled": "2032-05-28T07:00:00+0000"
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
            "guid": "sports-results-today-1", "type": "planning", "state": "scheduled", "pubstatus": "usable",
            "slugline": "sports-results",
            "name": "Sports Results for Today",
            "description_text": "<p><h1>Current Sports Results for Today 1</h1></p>",
            "planning_date": "2032-05-28T08:00:00+0000",
            "coverages": [{
                "coverage_id": "plan4_cov1",
                "firstcreated": "2018-05-28T05:00:00+0000",
                "workflow_status": "draft",
                "planning": {
                    "g2_content_type": "text",
                    "slugline": "sports-results-today-1-text",
                    "genre": [{"name": "Article (news)", "qcode": "Article"}],
                    "scheduled": "2032-05-28T08:00:00+0000"
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
    Scenario: Search for all keywords
        When we get "/agenda/search?itemType=planning&advanced={"all":"Weather Sydney"}"
        Then we get the following order
        """
        ["weather-today-sydney"]
        """
        When we get "/agenda/search?itemType=planning&advanced={"all":"Weather Sidebar"}"
        Then we get the following order
        """
        ["weather-today-belgrade"]
        """
        When we get "/agenda/search?itemType=planning&advanced={"all":"Weather Wellington"}"
        Then we get the following order
        """
        []
        """

        When we get "/agenda/search?itemType=planning&advanced={"all":"Weather Sydney","fields":["name"]}"
        Then we get the following order
        """
        ["weather-today-sydney"]
        """
        When we get "/agenda/search?itemType=planning&advanced={"all":"Weather Sydney","fields":["slugline"]}"
        Then we get the following order
        """
        []
        """
        When we get "/agenda/search?itemType=planning&advanced={"all":"Weather Today","fields":["slugline"]}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "weather-today-belgrade"]
        """
        When we get "/agenda/search?itemType=planning&advanced={"all":"Weather Sidebar","fields":["slugline"]}"
        Then we get the following order
        """
        ["weather-today-belgrade"]
        """
        When we get "/agenda/search?itemType=planning&advanced={"all":"Weather Sydney Current","fields":["description"]}"
        Then we get the following order
        """
        ["weather-today-sydney"]
        """
        When we get "/agenda/search?itemType=planning&advanced={"all":"Today Weather Report","fields":["description"]}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "weather-today-belgrade"]
        """

    @auth @admin
    Scenario: Search for any keywords
        When we get "/agenda/search?itemType=planning&advanced={"any":"Sydney Prague Belgrade Wellington"}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "weather-today-belgrade"]
        """
        When we get "/agenda/search?itemType=planning&advanced={"any":"Wellington Canberra"}"
        Then we get the following order
        """
        []
        """
        When we get "/agenda/search?itemType=planning&advanced={"any":"Sydney Prague Belgrade Wellington","fields":["name"]}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "weather-today-belgrade"]
        """
        When we get "/agenda/search?itemType=planning&advanced={"any":"Sydney Wellington","fields":["name"]}"
        Then we get the following order
        """
        ["weather-today-sydney"]
        """
        When we get "/agenda/search?itemType=planning&advanced={"any":"Sydney Prague Belgrade Wellington","fields":["slugline"]}"
        Then we get the following order
        """
        []
        """
        When we get "/agenda/search?itemType=planning&advanced={"any":"Story Sidebar","fields":["slugline"]}"
        Then we get the following order
        """
        ["weather-today-prague", "weather-today-belgrade"]
        """
        When we get "/agenda/search?itemType=planning&advanced={"any":"Sydney Prague Belgrade Wellington","fields":["description"]}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "weather-today-belgrade"]
        """
        When we get "/agenda/search?itemType=planning&advanced={"any":"Sydney Wellington","fields":["description"]}"
        Then we get the following order
        """
        ["weather-today-sydney"]
        """

    @auth @admin
    Scenario: Search for excluded keywords
        When we get "/agenda/search?itemType=planning&advanced={"exclude":"Belgrade Wellington Canberra"}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "sports-results-today-1"]
        """
        When we get "/agenda/search?itemType=planning&advanced={"exclude":"Weather"}"
        Then we get the following order
        """
        ["sports-results-today-1"]
        """
        When we get "/agenda/search?itemType=planning&advanced={"exclude":"Current","fields":["name"]}"
        Then we get the following order
        """
        ["weather-today-prague", "weather-today-belgrade", "sports-results-today-1"]
        """
        When we get "/agenda/search?itemType=planning&advanced={"exclude":"Story Sidebar","fields":["slugline"]}"
        Then we get the following order
        """
        ["weather-today-sydney", "sports-results-today-1"]
        """

    @auth @admin
    Scenario: Search multiple fields
        When we get "/agenda/search?itemType=planning&advanced={"all":"Sydney Australia Report","fields":["name","description"]}"
        Then we get the following order
        """
        ["weather-today-sydney"]
        """
