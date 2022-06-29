Feature: Agenda Search
    @auth @admin
    Scenario: Search Planning Only
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
            }
        }
        """
        And we post json to "/push"
        """
        {
            "guid": "plan1", "type": "planning", "state": "scheduled", "pubstatus": "usable",
            "event_item": "event1",
            "slugline": "New Press Conference",
            "name": "Prime minister press conference",
            "planning_date": "2018-05-28T05:00:00+0000"
        }
        """
        And we post json to "/push"
        """
        {
            "guid": "plan2", "type": "planning", "state": "scheduled", "pubstatus": "usable",
            "slugline": "New Press Conference",
            "name": "Prime minister press conference",
            "planning_date": "2018-05-28T06:00:00+0000"
        }
        """
        When we get "/agenda/search"
        Then we get the following order
        """
        ["event1", "plan2"]
        """
        When we get "/agenda/search?itemType=events"
        Then we get the following order
        """
        ["event1"]
        """
        When we get "/agenda/search?itemType=planning"
        Then we get the following order
        """
        ["plan1", "plan2"]
        """
