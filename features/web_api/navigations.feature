Feature: Navigations
    @auth @admin
    Scenario: Removes Navigations from Products when updating list of Navigations
        When we post form to "/navigations/new"
        """
        {
            "navigation": {
                "name": "Sports", "description": "Sports stories",
                "is_enabled": true, "product_type": "wire"
            }
        }
        """
        Then we store "NAV_ID" with item id
        When we post json to "/products/new"
        """
        {
            "name": "Sports", "description": "Sports stories",
            "query": "sports", "product_type": "wire"
        }
        """
        Then we store "PROD_ID" with item id
        When we post json to "/products/#PROD_ID#/navigations"
        """
        {
            "navigations": ["#NAV_ID#"]
        }
        """
        When we delete "/navigations/#NAV_ID#"
        And we get "/products"
        Then we get existing resource
        """
        [{
            "_id": "#PROD_ID#",
            "navigations": "__empty__"
        }]
        """
