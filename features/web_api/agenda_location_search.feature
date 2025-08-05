Feature: Agenda Search - Filter Locations Based on State

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
                {"qcode": "e", "name": "Entertainment"},
                {"qcode": "f", "name": "Finance"}
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
            "guid": "event4", "type": "event", "state": "killed", "pubstatus": "cancelled",
            "slugline": "Cancelled Melbourne Event",
            "name": "Cancelled Melbourne Event",
            "dates": {
                "start": "2018-05-28T04:00:00+0000",
                "end": "2018-05-28T05:00:00+0000",
                "tz": "Australia/Sydney"
            },
            "calendars": [{"qcode": "cal2", "name": "Calendar2"}],
            "subject": [
                {"code": "d2", "scheme": "sttdepartment", "name": "Dep2"},
                {"code": "s2", "scheme": "sttsubj", "name": "Sub2"},
                {"code": "e2", "scheme": "event_type", "name": "Music"}
            ],
            "place": [
                {"code": "VIC", "name": "Victoria"}
            ],
            "anpa_category": [
                {"qcode": "e", "name": "Entertainment"},
                {"qcode": "f", "name": "Finance"}
            ],
            "location": [{
                "name": "Cancelled Melbourne Location",
                "address": {
                    "city": "Melbourne",
                    "state": "Victoria",
                    "country": "Australia",
                    "line": ["Cancelled Street"],
                    "postal_code": "3000",
                    "type": "stadium",
                    "title": "Cancelled Melbourne Location",
                    "area": "Yarra Park"
                }
            }]
        }
        """

        And we post json to "/push"
        """
        {
            "guid": "event5", "type": "event", "state": "scheduled", "pubstatus": "usable",
            "slugline": "Empty Name Event",
            "name": "",
            "dates": {
                "start": "2018-05-28T04:00:00+0000",
                "end": "2018-05-28T05:00:00+0000",
                "tz": "Australia/Sydney"
            },
            "calendars": [{"qcode": "cal3", "name": "Calendar3"}],
            "subject": [
                {"code": "d3", "scheme": "sttdepartment", "name": "Dep3"},
                {"code": "s3", "scheme": "sttsubj", "name": "Sub3"},
                {"code": "e3", "scheme": "event_type", "name": "Art"}
            ],
            "place": [
                {"code": "ON", "name": "Ontario"}
            ],
            "anpa_category": [
                {"qcode": "e", "name": "Entertainment"},
                {"qcode": "f", "name": "Finance"}
            ],
            "location": [{
                "name": "",
                "address": {
                    "city": "",
                    "state": "Ontario",
                    "country": "Canada",
                    "line": ["Empty Street"],
                    "postal_code": "M5V 3L9",
                    "type": "museum",
                    "title": "Empty Location Name",
                    "area": "Downtown Toronto"
                }
            }]
        }
        """

    @auth @admin
    Scenario: Verify locations are filtered based on event state
        When we get "/agenda/search_locations"
        Then we get existing resource
        """
        {
            "regions": [
                {"type": "city", "country": "Australia", "state": "New South Wales", "name": "Sydney"}
            ],
            "places": [
                "Sydney Harbour Bridge"
            ]
        }
        """

    @auth @admin
    Scenario: Verify locations with empty names are not included in the response
        When we get "/agenda/search_locations"
        Then we get existing resource
        """
        {
            "regions": [
                {
                    "name": "New South Wales",
                    "country": "Australia",
                    "type": "state"
                },
                {
                    "name": "Australia",
                    "type": "country"
                }
            ],
            "places": []
        }
        """
