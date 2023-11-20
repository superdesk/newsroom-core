Feature: Agenda Multiday Search
    Background: Push content
        When we post json to "/push"
        """
        {
            "guid": "event1", "type": "event", "state": "scheduled", "pubstatus": "usable",
            "slugline": "New Press Conference", "name": "Prime minister press conference",
            "dates": {
                "start": "2023-11-14T04:00:00+0000",
                "end": "2023-11-17T05:00:00+0000",
                "tz": "Australia/Sydney"
            }
        }
        """
        And we post json to "/push"
        """
        {
            "guid": "event2", "type": "event", "state": "scheduled", "pubstatus": "usable",
            "slugline": "New Press Conference", "name": "Prime minister press conference",
            "dates": {
                "start": "2023-11-15T04:00:00+0000",
                "end": "2023-11-15T05:00:00+0000",
                "tz": "Australia/Sydney"
            }
        }
        """
        And we post json to "/push"
        """
        {
            "guid": "event3", "type": "event", "state": "scheduled", "pubstatus": "usable",
            "slugline": "New Press Conference", "name": "Prime minister press conference",
            "dates": {
                "start": "2023-11-16T04:00:00+0000",
                "end": "2023-11-16T05:00:00+0000",
                "tz": "Australia/Sydney"
            }
        }
        """

    @auth @admin
    Scenario: Search events
        When we get "/agenda/search?starts_before=2023-11-15"
        Then we get the following order
        """
        ["event1"]
        """
        When we get "/agenda/search?starts_before=2023-11-10"
        Then we get list with 0 items
        When we get "/agenda/search?ends_after=2023-11-16"
        Then we get the following order
        """
        ["event1", "event3"]
        """
        When we get "/agenda/search?ends_after=2023-11-18"
        Then we get list with 0 items
        When we get "/agenda/search?starts_before=2023-11-15&ends_after=2023-11-15"
        Then we get the following order
        """
        ["event1"]
        """
