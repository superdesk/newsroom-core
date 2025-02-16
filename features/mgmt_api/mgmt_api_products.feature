Feature: Management API - Products
    Scenario: Get company products
        When we post to this "/companies"
        """
        [{"name": "zzz company"}]
        """
        Then we get response code 201

        When we post to this "/products"
        """
        [{
            "name": "A fishy Product",
            "description": "a product for those interested in fish",
            "query": "fish",
            "product_type": "agenda"
        }]
        """
        Then we get response code 201

        When we get "/products"
        Then we get existing resource
        """
        {"_items": [
            {"name": "A fishy Product"}
        ]}
        """
        When we patch to this "/products/#products._id#"
        """
        {"description": "new description"}
        """
        Then we get response code 200

        When we post to this "companies/#companies._id#/products"
            """
            [
                {
                    "product": "#products._id#",
                    "seats": 5,
                    "link": true
                }
            ]
            """
            Then we get response code 201
