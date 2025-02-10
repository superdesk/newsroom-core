Feature: Management API
    Scenario: API is up and running
        When we get "/"
        Then we get existing resource
        """
        {"_links": {
            "child": [
                {"href": "users"},
                {"href": "companies"},
                {"href": "products"},
                {"href": "topics"},
                {"href": "navigations"}
            ]
        }}
        """

    Scenario: test auth without token
        Given empty auth token
        When we get "/"
        Then we get response code 401

        When we get "/users"
        Then we get response code 401

    Scenario: Create a navigation
        Given empty "navigations"
        When we post to "/navigations"
        """
        {
            "name": "navigation1",
            "description": "navigation1",
            "order": 1
        }
        """
        Then we get response code 201
        When we get "/navigations"
        Then we get existing resource
        """
        {
        "_items" :
            [
                {
                    "name": "navigation1",
                    "description": "navigation1",
                    "order": 1
                }
            ]
        }
        """

    Scenario: Delete a navigation
       Given empty "navigations"
        When we post to "/navigations"
        """
        [{
            "name": "navigation1",
            "description": "navigation1",
            "order": 1
        }]
        """
        When we delete latest
        Then we get response code 204


    Scenario: Update a navigation
        Given empty "navigations"
        When we post to "/navigations"
        """
        [{"name": "navigation1"}]
        """
        When we patch latest
        """
        {"name": "navigation2"}
        """
        Then we get updated response
        """
        {"name": "navigation2"}
        """


    Scenario: Create a topic
        Given empty "companies"
        When we post to "/companies"
        """
        {"name": "zzz company"}
        """
        Then we get response code 201
        When we post to "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena@wwe.com",
            "company": "#companies._id#"
        }
        """
        Then we get response code 201
        Given empty "topics"
        When we post to "/topics"
        """
        {
            "label": "topic1",
            "company": "#companies._id#",
            "topic_type": "wire",
            "query": "topic1",
            "is_global": true,
            "user": "#users._id#"
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
                    "user": "#users._id#"
                }
            ]
        }
        """


    Scenario: Delete a topic
        Given empty "companies"
        When we post to "/companies"
        """
        [{"name": "zzz company"}]
        """
        Then we get response code 201
        When we post to "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena@wwe.com",
            "company": "#companies._id#"
        }
        """
        Then we get response code 201
        Given empty "topics"
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
        Given empty "companies"
        When we post to "/companies"
        """
        [{"name": "zzz company"}]
        """
        Then we get response code 201
        When we post to "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena@wwe.com",
            "company": "#companies._id#"
        }
        """
        Then we get response code 201
        Given empty "topics"
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

        When we patch latest
        """
        {"subscribers": [{"user_id" :"#users._id#", "notification_type": "real-time"}]}
        """
        Then we get updated response
