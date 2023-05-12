Feature: User Permissions
    @auth @admin
    Scenario: Remove company from user should allow any section
        Given "navigations"
        """
        [{
            "_id": "59b4c5c61d41c8d736852fbf", "product_type": "wire", "is_enabled": true,
            "name": "All wire", "description": "All wire content"
        }, {
            "_id": "59b4c5c61d41c8d736852fbg", "product_type": "wire", "is_enabled": true,
            "name": "Sports", "description": "Sports content"
        }, {
            "_id": "59b4c5c61d41c8d736852fbh", "product_type": "agenda", "is_enabled": true,
            "name": "Sports", "description": "Sports coverages"
        }]
        """
        And "products"
        """
        [{
            "_id": "69b4c5c61d41c8d736852fbf", "product_type": "wire", "is_enabled": true,
            "name": "All wire", "query": "slugline:wire",
            "navigations": ["59b4c5c61d41c8d736852fbf"]
        }, {
            "_id": "69b4c5c61d41c8d736852fba", "product_type": "wire", "is_enabled": true,
            "name": "Sports content", "query": "slugline:sports",
            "navigations": ["59b4c5c61d41c8d736852fbf"]
        }, {
            "_id": "69b4c5c61d41c8d736852fbb", "product_type": "agenda", "is_enabled": true,
            "name": "Sports coverages", "query": "slugline:sports",
            "navigations": ["59b4c5c61d41c8d736852fbh"]
        }]
        """
        And "companies"
        """
        [{
            "_id": "1e65964bf5db68883df561b0", "company_type": "public",
            "name": "All Access Co.", "is_enabled": true,
            "sections": {"wire": true, "agenda": false},
            "products": [
                {"_id": "69b4c5c61d41c8d736852fbf", "section": "wire", "seats": 2},
                {"_id": "69b4c5c61d41c8d736852fba", "section": "wire", "seats": 2}
            ]
        }]
        """
        And "users"
        """
        [{
            "_id": "4e65964bf5db68883df561b0", "user_type": "company_admin",
            "company": "1e65964bf5db68883df561b0",
            "email": "test1@test.org", "first_name": "admin", "last_name": "admin",
            "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
            "is_validated": true, "is_enabled": true, "is_approved": true,
            "sections": {"wire": true, "agenda": false},
            "products": [
                {"_id": "69b4c5c61d41c8d736852fbf", "section": "wire"},
                {"_id": "69b4c5c61d41c8d736852fba", "section": "wire"}
            ]
        }]
        """
        When we get json from "/users/search"
        Then we get products assigned to items
        """
        {"4e65964bf5db68883df561b0": {
            "sections": ["wire"],
            "products": ["69b4c5c61d41c8d736852fbf", "69b4c5c61d41c8d736852fba"]
        }}
        """
        When we post json to "/users/4e65964bf5db68883df561b0"
        """
        {
            "company": null, "user_type": "administrator",
            "email": "test1@test.org", "first_name": "admin", "last_name": "admin",
            "sections": "wire,agenda",
            "products": "69b4c5c61d41c8d736852fbf,69b4c5c61d41c8d736852fba,69b4c5c61d41c8d736852fbb"
        }
        """
        When we get json from "/users/search"
        Then we get products assigned to items
        """
        {"4e65964bf5db68883df561b0": {
            "sections": ["wire", "agenda"],
            "products": ["69b4c5c61d41c8d736852fbf", "69b4c5c61d41c8d736852fba", "69b4c5c61d41c8d736852fbb"]
        }}
        """
