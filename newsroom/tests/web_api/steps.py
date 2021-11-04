from behave import then
from flask import json

from superdesk.tests.steps import assert_200, get_json_data


@then('we get the following order')
def step_impl_ordered_list(context):
    assert_200(context.response)
    response_data = (get_json_data(context.response) or {}).get("_items")
    ids = [item["_id"] for item in response_data]
    expected_order = json.loads(context.text)

    assert ids == expected_order, "{} != {}".format(",".join(ids), ",".join(expected_order))
