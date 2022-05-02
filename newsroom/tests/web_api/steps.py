from behave import then, when
from flask import json
from wooper.expect import expect_status_in

from superdesk.tests.steps import assert_200, get_json_data, apply_placeholders, get_prefixed_url, set_placeholder


def assert_ok(response):
    expect_status_in(response, [200, 201])


@then('we get the following order')
def step_impl_ordered_list(context):
    assert_200(context.response)
    response_data = (get_json_data(context.response) or {}).get("_items")
    ids = [item["_id"] for item in response_data]
    expected_order = json.loads(context.text)

    assert ids == expected_order, "{} != {}".format(",".join(ids), ",".join(expected_order))


@when('we post form to "{url}"')
def step_impl_when_post_form_to_url(context, url):
    url = apply_placeholders(context, url)
    data = json.loads(apply_placeholders(context, context.text))
    context.response = context.client.post(
        get_prefixed_url(context.app, url),
        data={
            key: json.dumps(val)
            for key, val in data.items()
        },
        headers=[
            header
            for header in context.headers
            if header[0] != "Content-Type"
        ]
    )

    assert_ok(context.response)


@when('we post json to "{url}"')
def step_impl_when_post_json_to_url(context, url):
    url = apply_placeholders(context, url)
    data = apply_placeholders(context, context.text)
    context.response = context.client.post(
        get_prefixed_url(context.app, url),
        data=data,
        headers=context.headers
    )

    assert_ok(context.response)


@then('we store "{tag}" with item id')
def step_impl_store_response_item_id(context, tag):
    data = get_json_data(context.response)
    set_placeholder(context, tag, data.get('_id'))
