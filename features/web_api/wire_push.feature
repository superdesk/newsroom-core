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
