from newsroom.tests.steps import *  # noqa
from behave import given


@given("empty auth token")
def given_empty_auth_token(context):
    """Removes the Authorization token from headers to simulate an unauthenticated request."""
    if not hasattr(context, "headers"):
        context.headers = []

    context.headers = [header for header in context.headers if header[0] != "Authorization"]
