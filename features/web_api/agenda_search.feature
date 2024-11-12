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
                {"qcode": "e", "name": "Entertainment"},
                {"qcode": "f", "name": "Finance"}
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
                {"qcode": "e", "name": "Entertainment"},
                {"qcode": "f", "name": "Finance"}
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
            }],
            "anpa_category": [
                {"qcode": "e", "name": "Entertainment"},
                {"qcode": "f", "name": "Finance"}
            ]
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

    @auth @admin
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
            "service": ["Entertainment", "Finance"],
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
                "matched_planning_items": ["plan1", "plan2"],
                "matched_coverages": "__none__"
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
                "matched_planning_items": ["plan1"],
                "matched_coverages": "__none__"
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
                "matched_planning_items": ["plan2"],
                "matched_coverages": ["plan2_cov1"]
            }
        }]}
        """

    @auth @admin
    Scenario: Search by location
        When we post json to "/push"
        """
        {
            "guid": "helsinki_event1", "type": "event", "state": "scheduled", "pubstatus": "usable",
            "name": "Helsingin Kirjamessut",
            "dates": {
                "start": "2018-05-28T04:00:00+0000",
                "end": "2018-05-28T05:00:00+0000",
                "tz": "Australia/Sydney"
            },
            "location": [{
                "name": "Helsingin Uusimaa Messukeskus",
                "address": {
                    "title": "Helsingin Uusimaa Messukeskus",
                    "line": ["Messuaukio 1"],
                    "city": "Helsinki", "state": "Uusimaa", "country": "Suomi",
                    "extra": {
                        "iso3166": "iso3166-1a2:FI",
                        "sttcity": "35",
                        "sttcountry": "1",
                        "sttlocationalias": "16179",
                        "sttstate": "31"
                    }
                }
            }]
        }
        """
        And we post json to "/push"
        """
        {
            "guid": "tuusula_event1", "type": "event", "state": "scheduled", "pubstatus": "usable",
            "name": "Tuusulan työpaikkamurhasta syytetty oli mielentilatutkimuksen mukaan syyntakeeton",
            "dates": {
                "start": "2018-06-28T04:00:00+0000",
                "end": "2018-06-28T05:00:00+0000",
                "tz": "Australia/Sydney"
            },
            "location": [{
                "name": "Itä-Uudenmaan käräjäoikeus",
                "address": {
                    "title": "Itä-Uudenmaan käräjäoikeus",
                    "city": "Tuusula", "state": "Uusimaa", "country": "Suomi",
                    "extra": {
                        "iso3166": "iso3166-1a2:FI",
                        "sttcity": "307",
                        "sttcountry": "1",
                        "sttlocationalias": "19558",
                        "sttstate": "31"
                    }
                }
            }]
        }
        """
        And we post json to "/push"
        """
        {
            "guid": "vaasa_event1", "type": "event", "state": "scheduled", "pubstatus": "usable",
            "name": "Pesäpallo: Miesten Superpesis, 1/3 pronssiottelu, klo 15 Hyvinkää-Joensuu",
            "dates": {
                "start": "2018-07-28T04:00:00+0000",
                "end": "2018-07-28T05:00:00+0000",
                "tz": "Australia/Sydney"
            },
            "location": [{
                "name": "Nightwishin stadionkonsertti Vaasassa",
                "address": {
                    "title": "Nightwishin stadionkonsertti Vaasassa",
                    "line": ["Rantamaantie"],
                    "city": "Vaasa", "state": "Pohjanmaa", "country": "Suomi",
                    "extra": {
                        "iso3166": "iso3166-1a2:FI",
                        "sttcity": "317",
                        "sttcountry": "1",
                        "sttlocationalias": "22376",
                        "sttstate": "40"
                    }
                }
            }]
        }
        """
        When we get "/agenda/search_locations"
        Then we get existing resource
        """
        {
            "regions": [
                {"type": "city", "country": "Australia", "state": "New South Wales", "name": "Sydney"},
                {"type": "state", "country": "Australia", "name": "New South Wales"},
                {"type": "country", "name": "Australia"},
                {"type": "city", "country": "Suomi", "state": "Uusimaa", "name": "Helsinki"},
                {"type": "city", "country": "Suomi", "state": "Uusimaa", "name": "Tuusula"},
                {"type": "state", "country": "Suomi", "name": "Uusimaa"},
                {"type": "city", "country": "Suomi", "state": "Pohjanmaa", "name": "Vaasa"},
                {"type": "state", "country": "Suomi", "name": "Pohjanmaa"},
                {"type": "country", "name": "Suomi"}
            ],
            "places": [
                "Sydney Harbour Bridge",
                "Helsingin Uusimaa Messukeskus",
                "It\u00e4-Uudenmaan k\u00e4r\u00e4j\u00e4oikeus",
                "Nightwishin stadionkonsertti Vaasassa"
            ]
        }
        """
        When we get "/agenda/search_locations?q=uus"
        Then we get existing resource
        """
        {
            "regions": [
                {"type": "city", "country": "Suomi", "state": "Uusimaa", "name": "Tuusula"},
                {"type": "state", "country": "Suomi", "name": "Uusimaa"}
            ],
            "places": [
                "Helsingin Uusimaa Messukeskus"
            ]
        }
        """
        When we get "/agenda/search?filter={\"location\":{\"type\":\"city\",\"name\":\"Helsinki\"}}"
        Then we get the following order
        """
        ["helsinki_event1"]
        """
        When we get "/agenda/search?filter={\"location\":{\"type\":\"state\",\"name\":\"Uusimaa\"}}"
        Then we get the following order
        """
        ["helsinki_event1", "tuusula_event1"]
        """
        When we get "/agenda/search?filter={\"location\":{\"type\":\"country\",\"name\":\"Suomi\"}}"
        Then we get the following order
        """
        ["helsinki_event1", "tuusula_event1", "vaasa_event1"]
        """
        When we get "/agenda/search?filter={\"location\":{\"name\":\"Helsingin Uusimaa Messukeskus\"}}"
        Then we get the following order
        """
        ["helsinki_event1"]
        """

    @auth @admin
    Scenario: Search should not match planning items (CPCN-666)
        When we get "/agenda/search?q=NOT service.name:Finance NOT service.name:Entertainment&date_from=2018-05-28"
        Then we get list with 0 items
