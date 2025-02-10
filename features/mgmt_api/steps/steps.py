from newsroom.tests.steps import *  # noqa
from behave import given


@given("empty auth token")
def given_empty_auth_token(context):
    print("empty auth token", context)
    context.headers = [header for header in context.headers if header[0] != "Authorization"]
