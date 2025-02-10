Feature: Management API - Topics
    Background: Setup companies and users
        Given empty "companies"
        When we post to "/companies"
        """
        [{"name": "zzz company"}]
        """
        Then we get response code 201
        When we post to "/users"
        """
        {
            "first_name": "Foo",
            "last_name": "Bar",
            "email": "foo@bar.org",
            "company": "#companies._id#",
            "user_type": "public"
        }
        """
        Then we get response code 201

    Scenario: Create a topic
        When we post to "/topics"
        """
        {
            "label": "topic1",
            "company": "#companies._id#",
            "topic_type": "wire",
            "query": "topic1",
            "is_global": true,
            "user": "#users._id#",
            "subscribers": [
                {"user_id": "#users._id#"}
            ]
        }
        """
        Then we get response code 201
        When we get "/topics"
        Then we get existing resource
        """
        {
        "_items" :
            [
                {
                    "label": "topic1",
                    "company": "#companies._id#",
                    "topic_type": "wire",
                    "query": "topic1",
                    "is_global": true,
                    "user": "#users._id#",
                    "subscribers": [
                        {"user_id": "#users._id#", "notification_type": "real-time"}
                    ]
                }
            ]
        }
        """

    Scenario: Delete a topic
        When we post to "/topics"
        """
        [{
            "label": "topic1",
            "company": "#companies._id#",
            "topic_type": "wire",
            "query": "topic1",
            "is_global": true,
            "user": "#users._id#"
        }]
        """
        When we delete latest
        Then we get response code 204

    Scenario: Update a topic
        When we post to "/topics"
        """
        [{
            "label": "topic1",
            "company": "#companies._id#",
            "topic_type": "wire",
            "query": "topic1",
            "is_global": true,
            "user": "#users._id#"
        }]
        """
        When we patch latest
        """
        {"label": "topic2"}
        """
        Then we get updated response
        """
        {"label": "topic2"}
        """

    Scenario: Topic with folder
        Given "topic_folders"
        """
        [
            {
                "name": "test",
                "section": "wire"
            }
        ]
        """
        Given "topics"
        """
        [
            {
                "label": "topic1",
                "company": "#companies._id#",
                "topic_type": "wire",
                "query": "topic1",
                "is_global": true,
                "user": "#users._id#",
                "folder": "#topic_folders._id#"
            }
        ]
        """
        When we get "/topics"
        Then we get list with 1 items

    Scenario: Validate if navigation exists
        When we post to "/topics"
        """
        {
            "label": "topic1",
            "company": "#companies._id#",
            "topic_type": "wire",
            "query": "topic1",
            "is_global": true,
            "user": "#users._id#",
            "navigation": ["619277ef8bbbbfac6034aab7"]
        }
        """
        Then we get response code 400

        When we post to "navigations"
        """
        {
            "name": "navigation1",
            "description": "navigation1",
            "order": 1
        }
        """
        Then we get response code 201

        When we post to "/topics"
        """
        {
            "label": "topic1",
            "company": "#companies._id#",
            "topic_type": "wire",
            "query": "topic1",
            "is_global": true,
            "user": "#users._id#",
            "navigation": ["#navigations._id#"]
        }
        """
        Then we get response code 201
