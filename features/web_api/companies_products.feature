Feature: Company Products
    Background: Setup companies and products
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
            "sections": {"wire": true, "agenda": true},
            "products": [
                {"_id": "69b4c5c61d41c8d736852fbf", "section": "wire", "seats": 2},
                {"_id": "69b4c5c61d41c8d736852fba", "section": "wire", "seats": 2},
                {"_id": "69b4c5c61d41c8d736852fbb", "section": "agenda", "seats": 2}
            ]
        }]
        """
        Given "users"
        """
        [{
            "_id": "4e65964bf5db68883df561b0", "user_type": "public",
            "company": "1e65964bf5db68883df561b0",
            "email": "test1@test.org", "first_name": "admin", "last_name": "admin",
            "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
            "is_validated": true, "is_enabled": true, "is_approved": true,
            "sections": {"wire": true, "agenda": true},
            "products": [
                {"_id": "69b4c5c61d41c8d736852fbf", "section": "wire"},
                {"_id": "69b4c5c61d41c8d736852fba", "section": "wire"},
                {"_id": "69b4c5c61d41c8d736852fbb", "section": "agenda"}
            ]
        }]
        """

    @auth @admin
    Scenario: Company product changes affect user products
        # 1. Make sure Company and User has access to ALL sections/products
        When we get "/companies/1e65964bf5db68883df561b0"
        Then we get existing resource
        """
        {
            "_id": "1e65964bf5db68883df561b0",
            "sections": {"wire": true, "agenda": true},
            "products": [
                {"_id": "69b4c5c61d41c8d736852fbf"},
                {"_id": "69b4c5c61d41c8d736852fba"},
                {"_id": "69b4c5c61d41c8d736852fbb"}
            ]
        }
        """
        When we get json from "/companies/1e65964bf5db68883df561b0/users"
        Then we get existing resource
        """
        [{
            "_id": "4e65964bf5db68883df561b0",
            "sections": {"wire": true, "agenda": true},
            "products": [
                {"_id": "69b4c5c61d41c8d736852fbf"},
                {"_id": "69b4c5c61d41c8d736852fba"},
                {"_id": "69b4c5c61d41c8d736852fbb"}
            ]
        }]
        """

        # 2. Remove access to product: All wire, 69b4c5c61d41c8d736852fbf
        When we post json to "/companies/1e65964bf5db68883df561b0/permissions"
        """
        {
            "name": "All Access Co. 2",
            "sections": {"wire": true, "agenda": true},
            "products": {"69b4c5c61d41c8d736852fba": true, "69b4c5c61d41c8d736852fbb": true}
        }
        """
        # Check company permissions
        When we get "/companies/1e65964bf5db68883df561b0"
        Then we get existing resource
        """
        {
            "_id": "1e65964bf5db68883df561b0",
            "sections": {"wire": true, "agenda": true},
            "products": [{"_id": "69b4c5c61d41c8d736852fba"}, {"_id": "69b4c5c61d41c8d736852fbb"}]
        }
        """
        # Check user permissions
        When we get json from "/companies/1e65964bf5db68883df561b0/users"
        Then we get existing resource
        """
        [{
            "_id": "4e65964bf5db68883df561b0",
            "sections": {"wire": true, "agenda": true},
            "products": [{"_id": "69b4c5c61d41c8d736852fba"}, {"_id": "69b4c5c61d41c8d736852fbb"}]
        }]
        """

        # 3. Remove access to section: wire
        When we post json to "/companies/1e65964bf5db68883df561b0/permissions"
        """
        {
            "name": "All Access Co. 2",
            "sections": {"wire": false, "agenda": true},
            "products": {"69b4c5c61d41c8d736852fba": true, "69b4c5c61d41c8d736852fbb": true}
        }
        """
        # Check company permissions
        When we get "/companies/1e65964bf5db68883df561b0"
        Then we get existing resource
        """
        {
            "_id": "1e65964bf5db68883df561b0",
            "sections": {"wire": false, "agenda": true},
            "products": [{"_id": "69b4c5c61d41c8d736852fbb"}]
        }
        """
        # Check user permissions
        When we get json from "/companies/1e65964bf5db68883df561b0/users"
        Then we get existing resource
        """
        [{
            "_id": "4e65964bf5db68883df561b0",
            "sections": {"wire": false, "agenda": true},
            "products": [{"_id": "69b4c5c61d41c8d736852fbb"}]
        }]
        """

        # 4. Re-add access to section: wire, & product: All wire, 69b4c5c61d41c8d736852fba
        When we post json to "/companies/1e65964bf5db68883df561b0/permissions"
        """
        {
            "name": "All Access Co. 2",
            "sections": {"wire": true, "agenda": true},
            "products": {"69b4c5c61d41c8d736852fba": true, "69b4c5c61d41c8d736852fbb": true}
        }
        """
        # Check company permissions
        When we get "/companies/1e65964bf5db68883df561b0"
        Then we get existing resource
        """
        {
            "_id": "1e65964bf5db68883df561b0",
            "sections": {"wire": true, "agenda": true},
            "products": [{"_id": "69b4c5c61d41c8d736852fba"}, {"_id": "69b4c5c61d41c8d736852fbb"}]
        }
        """
        # Check user permissions (has access to wire, but defaults products to disabled)
        When we get json from "/companies/1e65964bf5db68883df561b0/users"
        Then we get existing resource
        """
        [{
            "_id": "4e65964bf5db68883df561b0",
            "sections": {"wire": true, "agenda": true},
            "products": [{"_id": "69b4c5c61d41c8d736852fbb"}]
        }]
        """

    @auth @admin
    Scenario: Products are removed from user when Company is changed
        # 1. Make a new company for the user to change to
        Given "companies"
        """
        [{
            "_id": "1e65964bf5db68883df561b1", "company_type": "public",
            "name": "2nd Company", "is_enabled": true,
            "sections": {"wire": true, "agenda": false},
            "products": [
                {"_id": "69b4c5c61d41c8d736852fba", "section": "wire", "seats": 2}
            ]
        }]
        """
        When we get json from "/companies/1e65964bf5db68883df561b0/users"
        Then we get existing resource
        """
        [{
            "_id": "4e65964bf5db68883df561b0", "company": "1e65964bf5db68883df561b0",
            "sections": {"wire": true, "agenda": true},
            "products": [
                {"_id": "69b4c5c61d41c8d736852fbf"},
                {"_id": "69b4c5c61d41c8d736852fba"},
                {"_id": "69b4c5c61d41c8d736852fbb"}
            ]
        }]
        """

        # 2. Change the user company
        When we post json to "/users/4e65964bf5db68883df561b0"
        """
        {
            "company": "1e65964bf5db68883df561b1", "user_type": "public",
            "email": "test1@test.org", "first_name": "admin", "last_name": "admin",
            "sections": "wire,agenda",
            "products": "69b4c5c61d41c8d736852fbf,69b4c5c61d41c8d736852fba,69b4c5c61d41c8d736852fbb"
        }
        """

        # 3. Make sure agenda is disabled, and only 1 product remains
        When we get json from "/companies/1e65964bf5db68883df561b1/users"
        Then we get existing resource
        """
        [{
            "_id": "4e65964bf5db68883df561b0", "company": "1e65964bf5db68883df561b1",
            "sections": {"wire": true, "agenda": false},
            "products": [
                {"_id": "69b4c5c61d41c8d736852fba"}
            ]
        }]
        """
