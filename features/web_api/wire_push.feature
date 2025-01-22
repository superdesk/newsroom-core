Feature: Wire Push
    @auth @admin @notification
    Scenario: Websocket notifications sent on wire topic matches
        When we post json to "users/#CONTEXT_USER_ID#/topics"
        """
        {
            "label": "Weather",
            "subscribers": [{"user_id": "#CONTEXT_USER_ID#", "notification_type": "real-time"}],
            "is_global": false,
            "topic_type": "wire",
            "query": "weather"
        }
        """
        Then we get OK response
        And we store "TOPIC_ID" with item id
        When we post json to "/push"
        """
        {
            "guid": "article1", "type": "text",
            "headline": "weather",
            "firstcreated": "2050-11-27T08:00:57+0000",
            "body_html": "<p>The weather is happening somewhere</p>",
            "genre": [{"name": "News", "code": "news"}]
        }
        """
        Then we get OK response
        And we get notifications
        """
        [{
            "event": "topic_matches",
            "extra": {
                "item": {"_id": "article1"},
                "topics": ["#TOPIC_ID#"]
            }
        }]
        """

    @auth @admin
    Scenario: Support unknown fields on push wire
        When we post json to "/push"
        """
        {
            "guid": "c84653b1-f42c-4b67-9573-f348dfb58791",
            "version": "2",
            "type": "text",
            "byline": "mk",
            "located": "Prague",
            "versioncreated": "2024-11-25T16:15:02+0000",
            "language": "en",
            "headline": "test place cv",
            "urgency": 3,
            "pubstatus": "usable",
            "ednote": "test  place cv",
            "body_html": "<p>test &nbsp;place cv</p>",
            "slugline": "test place cv",
            "firstcreated": "2024-11-25T16:14:17+0000",
            "firstpublished": "2024-11-25T16:15:02+0000",
            "source": "test_desk",
            "annotations": [],
            "place": [{
                "scheme": "geonames",
                "code": "3067696",
                "name": "Prague",
                "state": "Prague",
                "country": "Czechia",
                "state_code": "52",
                "country_code": "CZ",
                "geometry_point": {
                    "type": "Point",
                    "coordinates": [50.08804, 14.42076]
                }
            }],
            "profile": "mk_profile",
            "priority": 6,
            "subject": [{"code": "01001000", "name": "archaeology"}],
            "service": [{"code": "f1", "name": "FIXME1"}],
            "description_html": "<p>test place cv</p>",
            "description_text": "test place cv",
            "copyrightholder": "",
            "copyrightnotice": "",
            "usageterms": "",
            "genre": [{"code": "Article", "name": "Article (news)"}],
            "charcount": 13,
            "wordcount": 3,
            "readtime": 0,
            "authors": [{
                "code": "65f9fb38884e530196d0841e",
                "name": "Mikayel Karapetyan",
                "role": "writer",
                "biography": "",
                "uri": "urn:sd-uat.test.superdesk.org:user:65f9fb38884e530196d0841e"
            }],
            "products": [
                {"code": "66083127884e530196d08944", "name": "text"},
                {"code": "67325ba5dba99664698eafa7", "name": "prod subj arch"}
            ]
        }
        """
        Then we get OK response
        When we get "/wire/c84653b1-f42c-4b67-9573-f348dfb58791?format=json"
        Then we get existing resource
        """
        {
            "_id": "c84653b1-f42c-4b67-9573-f348dfb58791",
            "authors": [{
                "code": "65f9fb38884e530196d0841e",
                "name": "Mikayel Karapetyan",
                "role": "writer",
                "biography": "",
                "uri": "urn:sd-uat.test.superdesk.org:user:65f9fb38884e530196d0841e"
            }],
            "genre": [{"code": "Article", "name": "Article (news)"}],
            "place": [{
                "scheme": "geonames",
                "code": "3067696",
                "name": "Prague",
                "state": "Prague",
                "country": "Czechia",
                "state_code": "52",
                "country_code": "CZ",
                "geometry_point": {
                    "type": "Point",
                    "coordinates": [50.08804, 14.42076]
                }
            }],
            "products": [
                {"code": "66083127884e530196d08944", "name": "text"},
                {"code": "67325ba5dba99664698eafa7", "name": "prod subj arch"}
            ],
            "service": [{"code": "f1", "name": "FIXME1"}],
            "subject": [{"code": "01001000", "name": "archaeology"}]
        }
        """
