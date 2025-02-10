Feature: Management API - Companies
    Scenario: Create a company
        Given empty "companies"
        When we post to "/companies"
        """
        {
            "name": "zzz company",
            "contact_name": "zzz company",
            "country": "Iceland",
            "contact_email": "contact@zzz.com",
            "phone": "99999999"
        }
        """
        Then we get response code 201
        When we get "/companies"
        Then we get existing resource
        """
        {
        "_items" :
            [
                {
                    "name": "zzz company",
                    "contact_name": "zzz company",
                    "country": "Iceland",
                    "contact_email": "contact@zzz.com",
                    "phone": "99999999"
                }
            ]
        }
        """

    Scenario: Delete a company
       Given empty "companies"
        When we post to "/companies"
        """
        [{"name": "zzz company"}]
        """
        When we delete latest
        Then we get response code 204

    Scenario: Update a compnay
        Given empty "companies"
        When we post to "/companies"
        """
        [{"name": "zzz company"}]
        """
        When we patch latest
        """
        {"name": "xyz company"}
        """
        Then we get updated response
        """
        {"name": "xyz company"}
        """

    Scenario: Create a company with default country
        Given empty "companies"
        When we post to "/companies"
        """
        {
            "name": "zzz company",
            "contact_name": "zzz company",
            "contact_email": "contact@zzz.com",
            "phone": "99999999"
        }
        """
        Then we get response code 201
        When we get "/companies"
        Then we get existing resource
        """
        {
        "_items" :
            [
                {
                    "name": "zzz company",
                    "contact_name": "zzz company",
                    "country": "CAN",
                    "contact_email": "contact@zzz.com",
                    "phone": "99999999"
                }
            ]
        }
        """

    Scenario: Validate company products section
        Given "products"
        """
        [
            {"name": "test", "query": "test", "product_type": "agenda"}
        ]
        """

        When we post to "/companies"
        """
        {
            "name": "zzz company",
            "contact_name": "zzz company",
            "contact_email": "contact@zzz.com",
            "phone": "99999999",
            "sections": {"wire": true, "agenda": true},
            "products": [
                {"_id": "#products._id#", "section": "wire"}
            ]
        }
        """
        Then we get response code 201

        When we get "/companies/#companies._id#"
        Then we get existing resource
        """
        {
            "products": [
                {"_id": "#products._id#", "section": "agenda", "seats": 0}
            ]
        }
        """

        When we post to "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena@wwe.com",
            "company": "#companies._id#",
            "sections": {
                "wire": true,
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


        When we patch "/companies/#companies._id#"
        """
        {
            "products": [
                {"_id": "#products._id#", "section": "wire"}
            ]
        }
        """
        Then we get response code 200

        When we get "/companies/#companies._id#"
        Then we get existing resource
        """
        {
            "products": [
                {"_id": "#products._id#", "section": "agenda", "seats": 0}
            ]
        }
        """

        When we get "/users/#users._id#"
        Then we get existing resource
        """
        {
            "products": [
                {"_id": "#products._id#", "section": "agenda"}
            ]
        }
        """
