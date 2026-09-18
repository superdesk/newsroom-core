Feature: Authorization Server
    @auth @admin
    Scenario: Valid client authenticate with success
        When we post json to "/oauth_clients/new"
        """
        {"name": "test_client"}
        """
        Then we store response in "CLIENT"
        When we logout
        When we do OAuth2 with id "#CLIENT._id#" and password "#CLIENT.password#"
        Then we get a valid oauth2 access token

    @auth @admin
	Scenario: Invalid client can't authenticate
        When we post json to "/oauth_clients/new"
        """
        {"name": "test_client_2"}
        """
        Then we store "CLIENT_ID2" with item id
        When we logout
        When we do OAuth2 with id "#CLIENT_ID2#" and password "bad_secret_pwd"
        Then we get error 401
        """
        {"error": "invalid_client"}
        """
