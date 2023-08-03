Feature: Agenda Events Advanced Search
    Background: Push events
        When we post json to "/push"
        """
        {
            "guid": "weather-today-sydney", "type": "event", "state": "scheduled", "pubstatus": "usable",
            "slugline": "current-weather-today",
            "name": "Sydney Australia Weather Today Current",
            "definition_short": "<p><h1>Current Sydney Weather Report for Today</h1></p>",
            "definition_long": "<p><h1>Current Sydney Weather Report for Today</h1></p>",
            "dates": {
                "start": "2032-05-28T04:00:00+0000",
                "end": "2032-05-28T05:00:00+0000",
                "tz": "Australia/Sydney"
            }
        }
        """
        And we post json to "/push"
        """
        {
            "guid": "weather-today-prague", "type": "event", "state": "scheduled", "pubstatus": "usable",
            "slugline": "current-weather-today",
            "name": "Prague Weather Today",
            "definition_short": "<p><h1>Current Prague Weather Report for Today</h1></p>",
            "definition_long": "<p><h1>Current Prague Weather Report for Today</h1></p>",
            "dates": {
                "start": "2032-05-28T05:00:00+0000",
                "end": "2032-05-28T06:00:00+0000",
                "tz": "Australia/Sydney"
            }
        }
        """
        And we post json to "/push"
        """
        {
            "guid": "weather-today-belgrade", "type": "event", "state": "scheduled", "pubstatus": "usable",
            "slugline": "current-weather-today",
            "name": "Belgrade Weather Today",
            "definition_short": "<p><h1>Current Belgrade Weather Report for Today</h1></p>",
            "definition_long": "<p><h1>Current Belgrade Weather Report for Today</h1></p>",
            "dates": {
                "start": "2032-05-28T06:00:00+0000",
                "end": "2032-05-28T07:00:00+0000",
                "tz": "Australia/Sydney"
            }
        }
        """
        And we post json to "/push"
        """
        {
            "guid": "sports-results-today-1", "type": "event", "state": "scheduled", "pubstatus": "usable",
            "slugline": "sports-results",
            "name": "Sports Results for Today",
            "definition_short": "<p><h1>Current Sports Results for Today 1</h1></p>",
            "definition_long": "<p><h1>Current Sports Results for Today 1</h1></p>",
            "dates": {
                "start": "2032-05-28T07:00:00+0000",
                "end": "2032-05-28T08:00:00+0000",
                "tz": "Australia/Sydney"
            }
        }
        """

    @auth @admin
    Scenario: Search for all keywords
        When we get "/agenda/search?itemType=events&advanced={"all":"Weather Sydney"}"
        Then we get the following order
        """
        ["weather-today-sydney"]
        """
        When we get "/agenda/search?itemType=events&advanced={"all":"Weather Wellington"}"
        Then we get the following order
        """
        []
        """
        When we get "/agenda/search?itemType=events&advanced={"all":"Weather Sydney","fields":["name"]}"
        Then we get the following order
        """
        ["weather-today-sydney"]
        """
        When we get "/agenda/search?itemType=events&advanced={"all":"Weather Sydney","fields":["slugline"]}"
        Then we get the following order
        """
        []
        """
        When we get "/agenda/search?itemType=events&advanced={"all":"Weather Today","fields":["slugline"]}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "weather-today-belgrade"]
        """
        When we get "/agenda/search?itemType=events&advanced={"all":"Weather Sydney Current","fields":["description"]}"
        Then we get the following order
        """
        ["weather-today-sydney"]
        """
        When we get "/agenda/search?itemType=events&advanced={"all":"Today Weather Report","fields":["description"]}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "weather-today-belgrade"]
        """

    @auth @admin
    Scenario: Search for any keywords
        When we get "/agenda/search?itemType=events&advanced={"any":"Sydney Prague Belgrade Wellington"}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "weather-today-belgrade"]
        """
        When we get "/agenda/search?itemType=events&advanced={"any":"Wellington Canberra"}"
        Then we get the following order
        """
        []
        """
        When we get "/agenda/search?itemType=events&advanced={"any":"Sydney Prague Belgrade Wellington","fields":["name"]}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "weather-today-belgrade"]
        """
        When we get "/agenda/search?itemType=events&advanced={"any":"Sydney Wellington","fields":["name"]}"
        Then we get the following order
        """
        ["weather-today-sydney"]
        """
        When we get "/agenda/search?itemType=events&advanced={"any":"Sydney Prague Belgrade Wellington","fields":["slugline"]}"
        Then we get the following order
        """
        []
        """
        When we get "/agenda/search?itemType=events&advanced={"any":"Sports Weather","fields":["slugline"]}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "weather-today-belgrade", "sports-results-today-1"]
        """
        When we get "/agenda/search?itemType=events&advanced={"any":"Sydney Prague Belgrade Wellington","fields":["description"]}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "weather-today-belgrade"]
        """
        When we get "/agenda/search?itemType=events&advanced={"any":"Sydney Wellington","fields":["description"]}"
        Then we get the following order
        """
        ["weather-today-sydney"]
        """

    @auth @admin
    Scenario: Search for excluded keywords
        When we get "/agenda/search?itemType=events&advanced={"exclude":"Belgrade Wellington Canberra"}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "sports-results-today-1"]
        """
        When we get "/agenda/search?itemType=events&advanced={"exclude":"Weather"}"
        Then we get the following order
        """
        ["sports-results-today-1"]
        """
        When we get "/agenda/search?itemType=events&advanced={"exclude":"Current","fields":["name"]}"
        Then we get the following order
        """
        ["weather-today-prague", "weather-today-belgrade", "sports-results-today-1"]
        """

    @auth @admin
    Scenario: Search multiple fields
        When we get "/agenda/search?itemType=events&advanced={"all":"Sydney Australia Report","fields":["name","description"]}"
        Then we get the following order
        """
        ["weather-today-sydney"]
        """
