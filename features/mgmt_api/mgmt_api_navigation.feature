Feature: Management API - Navigation
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
