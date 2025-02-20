Feature: Management API - Users
    Scenario: Create a user
        Given newsroom "products"
        """
        [
            {"name": "test", "query": "test"}
        ]
        """
        When we post to this "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena@wwe.com"
        }
        """
        Then we get error 400
        When we post to this "/companies"
        """
        [{"name": "zzz company"}]
        """
        Then we get response code 201
        When we post to this "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena@wwe.com",
            "company": "#companies._id#",
            "user_type": "company_admin",
            "sections": {
                "wire": true
            },
            "products": [
                {"section": "wire", "_id": "#products._id#"}
            ]
        }
        """
        Then we get response code 201
        When we post to this "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena1@wwe.com",
            "user_type": "administrator"
        }
        """
        Then we get response code 201
        When we get "/users"
        Then we get existing resource
        """
        {
        "_items" :
            [
                {
                    "first_name": "John",
                    "last_name": "Cena",
                    "email": "johncena@wwe.com",
                    "company": "#companies._id#",
                    "user_type": "company_admin",
                    "sections": {
                        "wire": true
                    },
                    "products": [
                        {"section": "wire", "_id": "__objectid__"}
                    ]
                },
                {
                    "first_name": "John",
                    "last_name": "Cena",
                    "email": "johncena1@wwe.com",
                    "user_type": "administrator"
                }
            ]
        }
        """

    Scenario: Update a user
        When we post to this "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena@wwe.com",
            "user_type": "administrator"
        }
        """
        When we patch latest
        """
        {"last_name": "wick"}
        """
        Then we get updated response
        """
        {"last_name": "wick"}
        """

    Scenario: Delete a user
        When we post to this "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena@wwe.com",
            "user_type": "administrator"
        }
        """
        When we delete latest
        Then we get ok response
        When we get "/users"
        Then we get existing resource
        """
        {
        "_items" :
            []
        }
        """
    Scenario: Validate product type
        Given newsroom "products"
        """
        [
            {"name": "test", "query": "test", "product_type": "agenda"}
        ]
        """
        And newsroom "companies"
        """
        [{"name": "zzz company"}]
        """

        When we post to this "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena@wwe.com",
            "company": "#companies._id#",
            "sections": {
                "agenda": true
            },
            "products": [
                {"_id": "#products._id#", "section": "wire"}
            ]
        }
        """
        Then we get response code 201

        When we get "/users/#users._id#"
        Then we get existing resource
        """
        {
            "products": [
                {"_id": "#products._id#", "section": "agenda"}
            ]
        }
        """

        When we patch to this "/users/#users._id#"
        """
        {
            "products": [
                {"section": "wire", "_id": "#products._id#"}
            ]
        }
        """
        Then we get response code 200

        When we get "/users/#users._id#"
        Then we get existing resource
        """
        {
            "products": [
                {"section": "agenda", "_id": "#products._id#"}
            ]
        }
        """
    Scenario: Validate locale

        Given newsroom "companies"
        """
        [{"name": "zzz company"}]
        """

        When we post to this "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena@wwe.com",
            "company": "#companies._id#",
            "locale": "fr"
        }
        """

        Then we get error 400

        When we post to this "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena@wwe.com",
            "company": "#companies._id#",
            "locale": "fr_CA"
        }
        """
        Then we get response code 201
    
    Scenario: Search case insensitive
        Given newsroom "users"
        """
        [
            {
                "first_name": "John",
                "last_name": "Cena",
                "email": "JohnCena@wwe.com",
                "user_type": "administrator"
            },
            {
                "first_name": "Alex",
                "last_name": "Billiam",
                "email": "alexbilliam@wwe.com",
                "user_type": "administrator"
            }
        ]
        """

        When we get "/users?where={"email": "johncena@wwe.com"}"
        Then we get list with 1 items

        When we get "/users?where={"email": "JohnCena@wwe.com"}"
        Then we get list with 1 items
