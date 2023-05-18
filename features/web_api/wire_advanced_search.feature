Feature: Wire Advanced Search
    Background: Push content
        Given "items"
        """
        [{
            "_id": "weather-today-sydney", "type": "text", "version": 1, "versioncreated": "#DATE#",
            "headline": "Sydney Weather Today Current",
            "slugline": "current-weather-today",
            "body_html": "<p><h1>Sydney Weather Report for Today</h1></p>"
        }, {
            "_id": "weather-today-prague", "type": "text", "version": 1, "versioncreated": "#DATE-1#",
            "headline": "Prague Weather Today",
            "slugline": "current-weather-today",
            "body_html": "<p><h1>Prague Weather Report for Today</h1></p>"
        }, {
            "_id": "weather-today-belgrade", "type": "text", "version": 1, "versioncreated": "#DATE-2#",
            "headline": "Belgrade Weather Today",
            "slugline": "current-weather-today",
            "body_html": "<p><h1>Belgrade Weather Report for Today</h1></p>"
        }, {
            "_id": "sports-results-today-1", "type": "text", "version": 1, "versioncreated": "#DATE-3#",
            "headline": "Sports Results for Today",
            "slugline": "sports-results",
            "body_html": "<p><h1>Sports Results for Today 1</h1></p>"
        }]
        """

    @auth @admin
    Scenario: Search for all keywords
        When we get "/wire/search?advanced_search={"all":"Weather Sydney"}"
        Then we get the following order
        """
        ["weather-today-sydney"]
        """
        When we get "/wire/search?advanced_search={"all":"Weather Wellington"}"
        Then we get the following order
        """
        []
        """
        When we get "/wire/search?advanced_search={"all":"Weather Sydney","fields":["headline"]}"
        Then we get the following order
        """
        ["weather-today-sydney"]
        """
        When we get "/wire/search?advanced_search={"all":"Weather Sydney","fields":["slugline"]}"
        Then we get the following order
        """
        []
        """
        When we get "/wire/search?advanced_search={"all":"Weather Today","fields":["slugline"]}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "weather-today-belgrade"]
        """
        When we get "/wire/search?advanced_search={"all":"Weather Sydney Report","fields":["body_html"]}"
        Then we get the following order
        """
        ["weather-today-sydney"]
        """

    @auth @admin
    Scenario: Search for any keywords
        When we get "/wire/search?advanced_search={"any":"Sydney Prague Belgrade Wellington"}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "weather-today-belgrade"]
        """
        When we get "/wire/search?advanced_search={"any":"Wellington Canberra"}"
        Then we get the following order
        """
        []
        """
        When we get "/wire/search?advanced_search={"any":"Sydney Prague Belgrade Wellington","fields":["headline"]}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "weather-today-belgrade"]
        """
        When we get "/wire/search?advanced_search={"any":"Sydney Prague Belgrade Wellington","fields":["slugline"]}"
        Then we get the following order
        """
        []
        """
        When we get "/wire/search?advanced_search={"any":"Sydney Prague Belgrade Wellington","fields":["body_html"]}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "weather-today-belgrade"]
        """

    @auth @admin
    Scenario: Search for excluded keywords
        When we get "/wire/search?advanced_search={"exclude":"Belgrade Wellington Canberra"}"
        Then we get the following order
        """
        ["weather-today-sydney", "weather-today-prague", "sports-results-today-1"]
        """
        When we get "/wire/search?advanced_search={"exclude":"Weather"}"
        Then we get the following order
        """
        ["sports-results-today-1"]
        """
        When we get "/wire/search?advanced_search={"exclude":"Weather","fields":["headline"]}"
        Then we get the following order
        """
        ["sports-results-today-1"]
        """

    @auth @admin @skip
    Scenario: Search multiple fields
        # This scenario currently fails, due to a technical limitation with `multi_match` queries
        # across fields with different analyzers
        # see: https://www.elastic.co/guide/en/elasticsearch/reference/7.10/query-dsl-multi-match-query.html#cross-field-analysis
        When we get "/wire/search?advanced_search={"all":"Sydney Current Report","fields":["headline","body_html"]}"
        Then we get the following order
        """
        ["weather-today-sydney"]
        """
