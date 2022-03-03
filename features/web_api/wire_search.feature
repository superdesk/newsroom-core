@wip
Feature: Wire Search
    @auth @admin
    Scenario: Sort items by descending publish date
        Given "items"
        """
        [{
            "_id": "urn:localhost:pos-3", "type": "text", "version": 1,
            "headline": "Weather", "slugline": "WEATHER", "body_html": "<p>Weather report</p>",
            "versioncreated": "#DATE-2#"
        }, {
            "_id": "urn:localhost:pos-2", "type": "text", "version": 1,
            "headline": "Weather", "slugline": "WEATHER", "body_html": "<p>Weather report</p>",
            "versioncreated": "#DATE-1#"
        }, {
            "_id": "urn:localhost:pos-1", "type": "text", "version": 1,
            "headline": "Weather", "slugline": "WEATHER", "body_html": "<p>Weather report</p>",
            "versioncreated": "#DATE#"
        }]
        """
        When we get "/wire/search"
        Then we get the following order
        """
        ["urn:localhost:pos-1", "urn:localhost:pos-2", "urn:localhost:pos-3"]
        """

    @auth @admin
    Scenario: Prepend embargoed items
        Given "items"
        """
        [{
            "_id": "embargo-4", "type": "text", "version": 1,
            "headline": "Weather", "slugline": "WEATHER", "body_html": "<p>Weather report</p>",
            "versioncreated": "#DATE-4#", "embargoed": "#DATE-1#"
        }, {
            "_id": "embargo-1", "type": "text", "version": 1,
            "headline": "Weather", "slugline": "WEATHER", "body_html": "<p>Weather report</p>",
            "versioncreated": "#DATE-3#", "embargoed": "#DATE+1#"
        }, {
            "_id": "published-3", "type": "text", "version": 1,
            "headline": "Weather", "slugline": "WEATHER", "body_html": "<p>Weather report</p>",
            "versioncreated": "#DATE-3#"
        }, {
            "_id": "published-2", "type": "text", "version": 1,
            "headline": "Weather", "slugline": "WEATHER", "body_html": "<p>Weather report</p>",
            "versioncreated": "#DATE-2#"
        }, {
            "_id": "embargo-2", "type": "text", "version": 1,
            "headline": "Weather", "slugline": "WEATHER", "body_html": "<p>Weather report</p>",
            "versioncreated": "#DATE-1#", "embargoed": "#DATE+2#"
        }, {
            "_id": "embargo-3", "type": "text", "version": 1,
            "headline": "Weather", "slugline": "WEATHER", "body_html": "<p>Weather report</p>",
            "versioncreated": "#DATE-1#", "embargoed": "#DATE#"
        }, {
            "_id": "published-1", "type": "text", "version": 1,
            "headline": "Weather", "slugline": "WEATHER", "body_html": "<p>Weather report</p>",
            "versioncreated": "#DATE#"
        }]
        """
        When we get "/wire/search"
        Then we get the following order
        """
        ["published-1", "embargo-2", "embargo-3", "published-2", "embargo-1", "published-3", "embargo-4"]
        """
        When we get "/wire/search?prepend_embargoed=0"
        Then we get the following order
        """
        ["published-1", "embargo-2", "embargo-3", "published-2", "embargo-1", "published-3", "embargo-4"]
        """
        When we get "/wire/search?prepend_embargoed=1"
        Then we get the following order
        """
        ["embargo-2", "embargo-1", "published-1", "embargo-3", "published-2", "published-3", "embargo-4"]
        """
        Given config update
        """
        {"PREPEND_EMBARGOED_TO_WIRE_SEARCH": true}
        """
        When we get "/wire/search"
        Then we get the following order
        """
        ["embargo-2", "embargo-1", "published-1", "embargo-3", "published-2", "published-3", "embargo-4"]
        """
        When we get "/wire/search?prepend_embargoed=0"
        Then we get the following order
        """
        ["published-1", "embargo-2", "embargo-3", "published-2", "embargo-1", "published-3", "embargo-4"]
        """
        When we get "/wire/search?prepend_embargoed=1"
        Then we get the following order
        """
        ["embargo-2", "embargo-1", "published-1", "embargo-3", "published-2", "published-3", "embargo-4"]
        """

    @auth @admin
    Scenario: Embargo based filters
        Given "items"
        """
        [{
            "_id": "embargo-2", "type": "text", "version": 1,
            "headline": "Weather", "slugline": "WEATHER", "body_html": "<p>Weather report</p>",
            "versioncreated": "#DATE-4#", "embargoed": "#DATE-1#"
        }, {
            "_id": "embargo-1", "type": "text", "version": 1,
            "headline": "Weather", "slugline": "WEATHER", "body_html": "<p>Weather report</p>",
            "versioncreated": "#DATE-3#", "embargoed": "#DATE+1#"
        }, {
            "_id": "published-1", "type": "text", "version": 1,
            "headline": "Weather", "slugline": "WEATHER", "body_html": "<p>Weather report</p>",
            "versioncreated": "#DATE-3#"
        }]
        """
        When we get "/wire/search?exclude_embargoed=0"
        Then we get the following order
        """
        ["embargo-1", "published-1", "embargo-2"]
        """
        When we get "/wire/search?exclude_embargoed=1"
        Then we get the following order
        """
        ["published-1", "embargo-2"]
        """
        When we get "/wire/search?embargoed_only=0"
        Then we get the following order
        """
        ["embargo-1", "published-1", "embargo-2"]
        """
        When we get "/wire/search?embargoed_only=1"
        Then we get the following order
        """
        ["embargo-1"]
        """
