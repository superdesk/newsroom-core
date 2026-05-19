Feature: Management API
    Scenario: API is up and running
        When we get "/"
        Then we get existing resource
        """
        {"_links": {
            "child": [
                    {
                        "href": "navigations",
                        "title": "navigations"
                    },
                    {
                        "href": "products",
                        "title": "products"
                    },
                    {
                        "href": "companies",
                        "title": "companies"
                    },
                    {
                        "href": "users",
                        "title": "users"
                    },
                    {
                        "href": "topics",
                        "title": "topics"
                    },
                    {
                        "href": "topic_folders",
                        "title": "topic_folders"
                    },
                    {
                        "href": "companies/<regex('[a-f0-9]{24}'):company_id>/products",
                        "title": "update_company_products"
                    },
                    {
                        "href": "companies/<regex('[a-f0-9]{24}'):company_id>/products",
                        "title": "get_company_products_endpoint"
                    }
                ]
        }}
        """

    Scenario: test auth without token
        Given empty auth token
        When we get "/"
        Then we get response code 401
