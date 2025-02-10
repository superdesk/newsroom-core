Feature: Management API - Products
    Scenario: Get company products
        Given empty "companies"
        When we post to "/companies"
        """
        [{"name": "zzz company"}]
        """
        Then we get response code 201

        Given empty "products"
        When we post to "/products"
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
        When we patch "/products/#products._id#"
        """
        {"description": "new description"}
        """
        Then we get response code 200

        When we post to "companies/#companies._id#/products"
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

        When we get "companies/#companies._id#/products"
        Then we get existing resource
        """
        {"_items": [
            {
                "name": "A fishy Product",
                "description": "new description",
                "query": "fish",
                "product_type": "agenda",
                "seats": 5
            }
        ]}
        """

        When we get "companies/#companies._id#"
        Then we get existing resource
        """
        {"products": [
            {"_id": "#products._id#", "section": "agenda", "seats": 5}
        ]}
        """

        When we post to "companies/#companies._id#/products"
        """
        [
            {
                "product": "#products._id#",
                "link": false
            }
        ]
        """
        Then we get response code 201
        When we get "companies/#companies._id#/products"
        Then we get existing resource
        """
        {"_items": []}
        """

        When we delete "/products/#products._id#"
        Then we get response code 204
